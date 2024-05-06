# Copyright (c) 2022, Frappe Technologies and contributors
# For license information, please see license.txt

import functools
import re

from rq.command import send_stop_job_command
from rq.exceptions import InvalidJobOperation, NoSuchJobError
from rq.job import Job
from rq.queue import Queue

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (
	cint,
	compare,
	convert_utc_to_system_timezone,
	create_batch,
	make_filter_dict,
)
from frappe.utils.background_jobs import get_queues, get_redis_conn

QUEUES = ["default", "long", "short"]
JOB_STATUSES = ["queued", "started", "failed", "finished", "deferred", "scheduled", "canceled"]


def check_permissions(method):
	@functools.wraps(method)
	def wrapper(*args, **kwargs):
		frappe.only_for("System Manager")
		job = args[0].job
		if not for_current_site(job):
			raise frappe.PermissionError

		return method(*args, **kwargs)

	return wrapper


class RQJob(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		arguments: DF.Code | None
		ended_at: DF.Datetime | None
		exc_info: DF.Code | None
		job_id: DF.Data | None
		job_name: DF.Data | None
		queue: DF.Literal["default", "short", "long"]
		started_at: DF.Datetime | None
		status: DF.Literal["queued", "started", "finished", "failed", "deferred", "scheduled", "canceled"]
		time_taken: DF.Duration | None
		timeout: DF.Duration | None
	# end: auto-generated types

	def load_from_db(self):
		try:
			job = Job.fetch(self.name, connection=get_redis_conn())
		except NoSuchJobError:
			raise frappe.DoesNotExistError

		if not for_current_site(job):
			raise frappe.PermissionError

		super(Document, self).__init__(serialize_job(job))
		self._job_obj = job

	@property
	def job(self):
		return self._job_obj

	@staticmethod
	def get_list(args):
		start = cint(args.get("start")) or 0
		page_length = cint(args.get("page_length")) or 20
		as_list = cint(args.get("as_list") or 0)
		fields = args.get("fields")

		if order_by := args.get("order_by"):
			*_, sort_key, sort_order = order_by.rsplit(" ", maxsplit=1)
			sort_key = sort_key.removeprefix("`tabRQ Job`.").strip("`")
			order_desc = "desc" in sort_order.lower()
		else:
			sort_key = "modified"
			order_desc = True

		matched_job_ids = RQJob.get_matching_job_ids(args)

		conn = get_redis_conn()
		jobs = [serialize_job(job) for job in Job.fetch_many(job_ids=matched_job_ids, connection=conn) if job]
		sorted_jobs = sorted(jobs, key=lambda j: j[sort_key], reverse=order_desc)[start : start + page_length]

		# Dont remove fields if as_list is True
		if fields and as_list:
			fields = tuple(f.removeprefix("`RQ Job`.").strip("`") for f in fields)
			for job_dict in sorted_jobs:
				for key in list(job_dict):
					if key not in fields + frappe.model.default_fields:
						job_dict.pop(key)

		if as_list:
			return list(list(j.values()) for j in sorted_jobs)

		return sorted_jobs

	@staticmethod
	def get_matching_job_ids(args) -> list[str]:
		filters = make_filter_dict(args.get("filters", {}))

		queues = _eval_filters(filters.get("queue"), QUEUES)
		statuses = _eval_filters(filters.get("status"), JOB_STATUSES)

		matched_job_ids = []
		for queue in get_queues():
			if not queue.name.endswith(tuple(queues)):
				continue
			for status in statuses:
				matched_job_ids.extend(fetch_job_ids(queue, status))

		return filter_current_site_jobs(matched_job_ids)

	@check_permissions
	def delete(self):
		self.job.delete()

	@check_permissions
	def requeue(self):
		self.job.requeue()

	@check_permissions
	def stop_job(self):
		try:
			send_stop_job_command(connection=get_redis_conn(), job_id=self.job_id)
		except InvalidJobOperation:
			frappe.msgprint(_("Job is not running."), title=_("Invalid Operation"))

	@staticmethod
	def get_count(args) -> int:
		return len(RQJob.get_matching_job_ids(args))

	# None of these methods apply to virtual job doctype, overriden for sanity.
	@staticmethod
	def get_stats(args):
		return {}

	def db_insert(self, *args, **kwargs):
		pass

	def db_update(self, *args, **kwargs):
		pass


def serialize_job(job: Job) -> frappe._dict:
	modified = job.last_heartbeat or job.ended_at or job.started_at or job.created_at
	job_kwargs = job.kwargs.get("kwargs", {})
	job_name = job_kwargs.get("job_type") or str(job.kwargs.get("job_name"))
	if job_name == "frappe.utils.background_jobs.run_doc_method":
		doctype = job_kwargs.get("doctype")
		doc_method = job_kwargs.get("doc_method")
		if doctype and doc_method:
			job_name = f"{doctype}.{doc_method}"

	# function objects have this repr: '<function functionname at 0xmemory_address >'
	# This regex just removes unnecessary things around it.
	if matches := re.match(r"<function (?P<func_name>.*) at 0x.*>", job_name):
		job_name = matches.group("func_name")

	return frappe._dict(
		name=job.id,
		job_id=job.id,
		queue=job.origin.rsplit(":", 1)[1],
		job_name=job_name,
		status=job.get_status(),
		started_at=convert_utc_to_system_timezone(job.started_at) if job.started_at else -1,
		ended_at=convert_utc_to_system_timezone(job.ended_at) if job.ended_at else -1,
		time_taken=(job.ended_at - job.started_at).total_seconds() if job.ended_at else -1,
		exc_info=job.exc_info,
		arguments=frappe.as_json(job.kwargs),
		timeout=job.timeout,
		creation=convert_utc_to_system_timezone(job.created_at),
		modified=convert_utc_to_system_timezone(modified),
		_comment_count=0,
		owner=job.kwargs.get("user"),
		modified_by=job.kwargs.get("user"),
	)


def for_current_site(job: Job) -> bool:
	return job.kwargs.get("site") == frappe.local.site


def filter_current_site_jobs(job_ids: list[str]) -> list[str]:
	site = frappe.local.site

	return [j for j in job_ids if j.startswith(site)]


def _eval_filters(filter, values: list[str]) -> list[str]:
	if filter:
		operator, operand = filter
		return [val for val in values if compare(val, operator, operand)]
	return values


def fetch_job_ids(queue: Queue, status: str) -> list[str]:
	registry_map = {
		"queued": queue,  # self
		"started": queue.started_job_registry,
		"finished": queue.finished_job_registry,
		"failed": queue.failed_job_registry,
		"deferred": queue.deferred_job_registry,
		"scheduled": queue.scheduled_job_registry,
		"canceled": queue.canceled_job_registry,
	}

	registry = registry_map.get(status)
	if registry is not None:
		job_ids = registry.get_job_ids()
		return [j for j in job_ids if j]

	return []


@frappe.whitelist()
def remove_failed_jobs():
	frappe.only_for("System Manager")
	for queue in get_queues():
		fail_registry = queue.failed_job_registry
		failed_jobs = filter_current_site_jobs(fail_registry.get_job_ids())

		# Delete in batches to avoid loading too many things in memory
		conn = get_redis_conn()
		for job_ids in create_batch(failed_jobs, 100):
			for job in Job.fetch_many(job_ids=job_ids, connection=conn):
				job and fail_registry.remove(job, delete_job=True)


def get_all_queued_jobs():
	jobs = []
	for q in get_queues():
		jobs.extend(q.get_jobs())

	return [job for job in jobs if for_current_site(job)]


@frappe.whitelist()
def stop_job(job_id):
	frappe.get_doc("RQ Job", job_id).stop_job()


@frappe.whitelist()
def requeue_job(job_id):
	frappe.get_doc("RQ Job", job_id).requeue()
