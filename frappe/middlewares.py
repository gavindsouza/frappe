# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

from __future__ import unicode_literals

import frappe
import os
from werkzeug.exceptions import NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from frappe.utils import get_site_name, cstr

import cv2
import datetime
from mimetypes import guess_type
from frappe.utils.image import image_resize

class StaticDataMiddleware(SharedDataMiddleware):
	def __call__(self, environ, start_response):
		self.environ = environ
		return super(StaticDataMiddleware, self).__call__(environ, start_response)

	def get_directory_loader(self, directory):
		def loader(path):
			site = get_site_name(frappe.app._site or self.environ.get('HTTP_HOST'))
			path = os.path.join(directory, site, 'public', 'files', cstr(path))
			if os.path.isfile(path):
				return os.path.basename(path), self._opener(path)
			else:
				raise NotFound
				# return None, None

		return loader


class ImageMiddleware:
	def dummp(self, path):
		frappe.logger("middleware").debug(f"{path}: {guess_type(path)}")

		if "image" in guess_type(path)[0]:
			try:
				img = image_resize(cv2.imread(path), height=100)
				img = cv2.imencode('.jpg', img)[1]
				frappe.local.response = img
				# return (
				# 	img.tobytes(),
				# 	datetime.datetime.utcnow(),
				# 	img.size,
				# )
			except:
				pass
