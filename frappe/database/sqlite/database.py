import re
import sqlite3
from typing import List, Tuple, Union

import frappe
from frappe.database.database import Database
from frappe.database.sqlite.schema import SQLiteTable
from frappe.utils import cstr, get_table_name


class SQLiteDatabase(Database):
	ProgrammingError = sqlite3.ProgrammingError
	TableMissingError = sqlite3.ProgrammingError
	OperationalError = sqlite3.OperationalError
	InternalError = sqlite3.InternalError
	SQLError = sqlite3.ProgrammingError
	DataError = sqlite3.DataError

	def __init__(self, host=None, user=None, password=None, ac_name=None, use_default=0, port=None):
		self.setup_type_map()
		# self.host = host or frappe.conf.db_host or '127.0.0.1'
		# self.port = port or frappe.conf.db_port or ''
		# self.user = user or frappe.conf.db_name
		# self.db_name = frappe.conf.db_name
		self._conn = None
		self.database_file = frappe.get_site_path("private", "database.sqlite3")

		# if ac_name:
		# 	self.user = ac_name or frappe.conf.db_name

		# if use_default:
		# 	self.user = frappe.conf.db_name

		self.transaction_writes = 0
		self.auto_commit_on_many_writes = 0

		# self.password = password or frappe.conf.db_password
		self.value_cache = {}

	def setup_type_map(self):
		self.db_type = 'sqlite'
		self.type_map = {
			'Currency':		('decimal', '18,6'),
			'Int':			('bigint', None),
			'Long Int':		('bigint', None),
			'Float':		('decimal', '18,6'),
			'Percent':		('decimal', '18,6'),
			'Check':		('smallint', None),
			'Small Text':	('text', ''),
			'Long Text':	('text', ''),
			'Code':			('text', ''),
			'Text Editor':	('text', ''),
			'Markdown Editor':	('text', ''),
			'HTML Editor':	('text', ''),
			'Date':			('date', ''),
			'Datetime':		('timestamp', None),
			'Time':			('time', '6'),
			'Text':			('text', ''),
			'Data':			('varchar', self.VARCHAR_LEN),
			'Link':			('varchar', self.VARCHAR_LEN),
			'Dynamic Link':	('varchar', self.VARCHAR_LEN),
			'Password':		('text', ''),
			'Select':		('varchar', self.VARCHAR_LEN),
			'Rating':		('smallint', None),
			'Read Only':	('varchar', self.VARCHAR_LEN),
			'Attach':		('text', ''),
			'Attach Image':	('text', ''),
			'Signature':	('text', ''),
			'Color':		('varchar', self.VARCHAR_LEN),
			'Barcode':		('text', ''),
			'Geolocation':	('text', ''),
			'Duration':		('decimal', '18,6'),
			'Icon':			('varchar', self.VARCHAR_LEN)
		}

	def get_connection(self):
		conn = sqlite3.connect(self.database_file, isolation_level="DEFERRED")
		return conn

	def connect(self):
		"""Connects to a database as set in `site_config.json`."""
		self.cur_db_name = self.database_file
		self._conn = self.get_connection()
		self._cursor = self._conn.cursor()
		frappe.local.rollback_observers = []

	def escape(self, s, percent=True):
		"""Excape quotes and percent in given string."""
		if isinstance(s, bytes):
			s = s.decode('utf-8')

		if percent:
			s = s.replace("?", "??")

		s = s.encode('utf-8')

		return s

	def get_database_size(self):
		''''Returns database size in MB'''
		db_size = self.sql("SELECT (pg_database_size(%s) / 1024 / 1024) as database_size",
			self.db_name, as_dict=True)
		return db_size[0].get('database_size')

	# pylint: disable=W0221
	def sql(self, *args, **kwargs):
		if args:
			# since tuple is immutable
			args = list(args)
			args[0] = modify_query(args[0])
			args = tuple(args)
		elif kwargs.get('query'):
			kwargs['query'] = modify_query(kwargs.get('query'))

		return super().sql(*args, **kwargs)

	def execute_query(self, query, values=None):
		query = query.replace('%s', '?')
		try:
			if isinstance(values, dict):
				query = query % {x: f"'{y}'" for x,y in values.items()}
		except TypeError:
			pass
		return self._cursor.execute(query, values)

	def get_db_table_columns(self, table):
		"""Returns list of column names from given table."""
		columns = frappe.cache().hget('table_columns', table)
		if columns is None:
			curr = self._conn.execute(f'select * from {table}')
			columns = [description[0] for description in curr.description]
			if columns:
				frappe.cache().hset('table_columns', table, columns)

		return columns

	def is_syntax_error(self, *args, **kwargs):
		pass

	def get_tables(self):
		return [d[0] for d in self.sql("SELECT name FROM sqlite_master WHERE type='table'")]

	def format_date(self, date):
		if not date:
			return '0001-01-01'

		if not isinstance(date, str):
			date = date.strftime('%Y-%m-%d')

		return date

	# column type
	@staticmethod
	def is_type_number(code):
		return code in ['int', 'decimal', 'float']

	@staticmethod
	def is_type_datetime(code):
		return code in ['datetime', 'timestamp']

	# exception type
	@staticmethod
	def is_deadlocked(e):
		return isinstance(e, sqlite3.OperationalError) and "locked" in str(e)

	# @staticmethod
	# def is_timedout(e):
	# 	return

	# @staticmethod
	# def is_table_missing(e):
	# 	return getattr(e, 'pgcode', None) == '42P01'

	# @staticmethod
	# def is_missing_column(e):
	# 	return getattr(e, 'pgcode', None) == '42703'

	# @staticmethod
	# def is_access_denied(e):
	# 	return e.pgcode == '42501'

	# @staticmethod
	# def cant_drop_field_or_key(e):
	# 	return e.pgcode.startswith('23')

	@staticmethod
	def is_duplicate_entry(e):
		return isinstance(e, sqlite3.OperationalError) and "duplicate column name" in str(e)

	@staticmethod
	def is_primary_key_violation(self, e):
		return self.is_duplicate_entry(e) and 'PRIMARY' in cstr(e.args[1])

	@staticmethod
	def is_unique_key_violation(self, e):
		return self.is_duplicate_entry(e) and 'Duplicate' in cstr(e.args[1])

	@staticmethod
	def is_duplicate_fieldname(e):
		return isinstance(e, sqlite3.OperationalError) and "duplicate column name" in str(e)

	# @staticmethod
	# def is_data_too_long(e):
	# 	return e.pgcode == '22001'

	def rename_table(self, old_name: str, new_name: str) -> Union[List, Tuple]:
		old_name = get_table_name(old_name)
		new_name = get_table_name(new_name)
		return self.sql(f"ALTER TABLE `{old_name}` RENAME TO `{new_name}`")

	def describe(self, doctype: str)-> Union[List, Tuple]:
		table_name = get_table_name(doctype)
		return self.sql(f"SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_NAME = '{table_name}'")

	def change_column_type(self, table: str, column: str, type: str) -> Union[List, Tuple]:
		table_name = get_table_name(table)
		return self.sql(f'ALTER TABLE "{table_name}" ALTER COLUMN "{column}" TYPE {type}')

	def create_auth_table(self):
		self.sql("""create table if not exists "__Auth" (
				"doctype" VARCHAR(140) NOT NULL,
				"name" VARCHAR(255) NOT NULL,
				"fieldname" VARCHAR(140) NOT NULL,
				"password" TEXT NOT NULL,
				"encrypted" INT NOT NULL DEFAULT 0,
				PRIMARY KEY ("doctype", "name", "fieldname")
			)""")


	def create_global_search_table(self):
		if not '__global_search' in self.get_tables():
			self.sql('''create table "__global_search"(
				doctype varchar(100),
				name varchar({0}),
				title varchar({0}),
				content text,
				route varchar({0}),
				published int not null default 0,
				unique (doctype, name))'''.format(self.VARCHAR_LEN))

	def create_user_settings_table(self):
		self.sql("""create table if not exists "__UserSettings" (
			"user" VARCHAR(180) NOT NULL,
			"doctype" VARCHAR(180) NOT NULL,
			"data" TEXT,
			UNIQUE ("user", "doctype")
			)""")

	def create_help_table(self):
		self.sql('''CREATE TABLE "help"(
				"path" varchar(255),
				"content" text,
				"title" text,
				"intro" text,
				"full_path" text)''')
		self.sql('''CREATE INDEX IF NOT EXISTS "help_index" ON "help" ("path")''')

	def updatedb(self, doctype, meta=None):
		"""
		Syncs a `DocType` to the table
		* creates if required
		* updates columns
		* updates indices
		"""
		res = self.sql("select issingle from `tabDocType` where name='{}'".format(doctype))
		if not res:
			raise Exception('Wrong doctype {0} in updatedb'.format(doctype))

		if not res[0][0]:
			db_table = SQLiteTable(doctype, meta)
			db_table.validate()

			self.commit()
			db_table.sync()
			self.begin()

	@staticmethod
	def get_on_duplicate_update(key='name'):
		if isinstance(key, list):
			key = '", "'.join(key)
		return 'ON CONFLICT ("{key}") DO UPDATE SET '.format(
			key=key
		)

	def check_transaction_status(self, query):
		pass

	def has_index(self, table_name, index_name):
		return self.sql(f"SELECT 1 FROM sqlite_master WHERE tbl_name = '{table_name}' and name = 'index_name' and type = 'index' limit 1")

	def add_index(self, doctype, fields, index_name=None):
		"""Creates an index with given fields if not already created.
		Index name will be `fieldname1_fieldname2_index`"""
		index_name = index_name or self.get_index_name(fields)
		table_name = 'tab' + doctype

		self.commit()
		self.sql("""CREATE INDEX IF NOT EXISTS "{}" ON `{}`("{}")""".format(index_name, table_name, '", "'.join(fields)))

	def add_unique(self, doctype, fields, constraint_name=None):
		if isinstance(fields, str):
			fields = [fields]
		if not constraint_name:
			constraint_name = "unique_" + "_".join(fields)

		if not self.sql("""
			SELECT CONSTRAINT_NAME
			FROM information_schema.TABLE_CONSTRAINTS
			WHERE table_name=%s
			AND constraint_type='UNIQUE'
			AND CONSTRAINT_NAME=%s""",
			('tab' + doctype, constraint_name)):
				self.commit()
				self.sql("""ALTER TABLE `tab%s`
					ADD CONSTRAINT %s UNIQUE (%s)""" % (doctype, constraint_name, ", ".join(fields)))

	def get_table_columns_description(self, table_name):
		"""Returns list of column and its description"""
		mappings = {
			"dflt_value": "default",
			"cid": "index",
			"pk": "unique",
		}
		pragma_values = self.sql(f"PRAGMA table_info('{table_name}')", as_dict=1)

		for current, standard in mappings.items():
			for column_type in pragma_values:
				column_type[standard] = column_type.pop(current, None)

		return pragma_values

	def get_database_list(self, target):
		return [d[0] for d in self.sql("SELECT datname FROM pg_database;")]

def modify_query(query):
	""""Modifies query according to the requirements of postgres"""
	# replace ` with " for definitions
	query = str(query)
	query = query.replace('`', '"')
	query = replace_locate_with_strpos(query)
	# select from requires ""
	if re.search('from tab', query, flags=re.IGNORECASE):
		query = re.sub('from tab([a-zA-Z]*)', r'from "tab\1"', query, flags=re.IGNORECASE)

	return query

def replace_locate_with_strpos(query):
	# strpos is the locate equivalent in postgres
	if re.search(r'locate\(', query, flags=re.IGNORECASE):
		query = re.sub(r'locate\(([^,]+),([^)]+)\)', r'strpos(\2, \1)', query, flags=re.IGNORECASE)
	return query
