from typing import Any
from frappe.model.document import Document, LinkField, DynamicLinkField
from frappe.utils.nestedset import NestedSet


class SugaredDocument(Document):
	def __getattr__(self, name):
		if (
			name != '_lazy_load' and self._lazy_load
		) and (
			not name.startswith('__')
		):
			self.load_from_db()
			self._lazy_load = False
		return super().__getattr__(name)

	def __getattribute__(self, name: str) -> Any:
		value = object.__getattribute__(self, name)

		if hasattr(value, '__get__') and not callable(value):
			value = value.__get__(self, self.__class__)

		return value

	def __setattribute__(self, name, value):
		try:
			obj = object.__getattribute__(self, name)
		except AttributeError:
			pass
		else:
			if hasattr(obj, '__set__'):
				return obj.__set__(self, value)
		return object.__setattr__(self, name, value)

	__setattr__ = __setattribute__

	def get(self, key=None, filters=None, limit=None, default=None):
		ret = super().get(key, filters, limit, default)
		if isinstance(ret, (LinkField, DynamicLinkField)):
			return ret.value
		return ret

	def set(self, key, value, as_value=False):
		if isinstance(value, list) and not as_value:
			self.__dict__[key] = []
			self.extend(key, value)
		else:
			obj = super().get(key)
			if isinstance(obj, (LinkField, DynamicLinkField)):
				setattr(self, key, value)
			else:
				self.__dict__[key] = value


class SugaredNestedSet(NestedSet, SugaredDocument):
	pass

