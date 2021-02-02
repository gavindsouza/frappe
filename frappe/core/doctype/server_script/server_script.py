# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import ast

import frappe
from frappe.model.document import Document
from frappe.utils.safe_exec import safe_exec
from frappe import _

# TODO: sync_jobs for server scriptt: scehduled

class ServerScript(Document):
	def validate(self):
		frappe.only_for('Script Manager', True)
		ast.parse(self.script)
		self.sync_scheduled_jobs()

	def sync_scheduled_jobs(self):
		self.load_doc_before_save()
		before_save = self.get_doc_before_save()

		before_events_dict = {x.event: x.scheduled_job for x in before_save.scheduled_events}
		after_events_dict = {x.event: x.scheduled_job for x in self.scheduled_events}
		all_events = set(before_events_dict) | set(after_events_dict)

		scheduled_events_changed = {
			event: (False if (before_events_dict.get(event) == after_events_dict.get(event)) else before_events_dict.get(event)) for event in all_events
		}

		if any(scheduled_events_changed.values()):
			for event, changed in scheduled_events_changed.items():
				if changed:
					does_exist = after_events_dict.get(event)
					if not does_exist:
						frappe.delete_doc_if_exists("Scheduled Job Type", changed, force=True)

		if self.has_value_changed("disabled"):
			frappe.db.update(
				"Scheduled Job Type",
				{"method": ("in", [x.scheduled_job for x in self.scheduled_events])},
				"stopped",
				self.disabled
			)

	@staticmethod
	def on_update():
		frappe.cache().delete_value('server_script_map')

	def execute_method(self):
		if self.script_type == 'API':
			# validate if guest is allowed
			if frappe.session.user == 'Guest' and not self.allow_guest:
				raise frappe.PermissionError
			_globals, _locals = safe_exec(self.script)
			return _globals.frappe.flags # output can be stored in flags
		else:
			# wrong report type!
			raise frappe.DoesNotExistError

	def execute_doc(self, doc):
		# execute event
		safe_exec(self.script, None, dict(doc = doc))

	def execute_scheduled_method(self):
		if self.script_type == 'Scheduler Event':
			safe_exec(self.script)
		else:
			# wrong report type!
			raise frappe.DoesNotExistError

	def get_permission_query_conditions(self, user):
		locals = {"user": user, "conditions": ""}
		safe_exec(self.script, None, locals)
		if locals["conditions"]:
			return locals["conditions"]


@frappe.whitelist()
def setup_scheduler_events(script_name, frequency):
	method = frappe.scrub('{0}-{1}'.format(script_name, frequency))
	scheduled_script = frappe.db.get_value('Scheduled Job Type', {"method": method})

	if not scheduled_script:
		doc = frappe.get_doc({
			"doctype": "Scheduled Job Type",
			"method": method,
			"frequency": frequency,
			"server_script": script_name
		}).insert()

		frappe.msgprint(_('Enabled scheduled execution for script {0}').format(script_name))

	else:
		doc = frappe.get_doc('Scheduled Job Type', scheduled_script)
		doc.update({
			"doctype": "Scheduled Job Type",
			"method": method,
			"frequency": frequency,
			"server_script": script_name
		}).save()

		frappe.msgprint(_('Scheduled execution for script {0} has updated').format(script_name))

	server_script = frappe.get_doc("Server Script", script_name)
	server_script.append("scheduled_events", {"event": frequency, "scheduled_job": method})
	server_script.save()
