import os

import frappe
import sqlite3


def setup_database(force, source_sql=None, verbose=False):

	# root_conn = {}
	# root_conn.sql("DROP DATABASE IF EXISTS `{0}`".format(frappe.conf.db_name))
	# root_conn.sql("DROP USER IF EXISTS {0}".format(frappe.conf.db_name))
	# root_conn.sql("CREATE DATABASE `{0}`".format(frappe.conf.db_name))
	# root_conn.sql("CREATE user {0} password '{1}'".format(frappe.conf.db_name,
	# 	frappe.conf.db_password))
	# root_conn.sql("GRANT ALL PRIVILEGES ON DATABASE `{0}` TO {0}".format(frappe.conf.db_name))
	# root_conn.close()

	bootstrap_database(frappe.conf.db_name, verbose, source_sql=source_sql)
	frappe.connect()

def bootstrap_database(db_name, verbose, source_sql=None):
	frappe.connect(db_name=db_name)

	import_db_from_sql(source_sql, verbose)
	frappe.connect(db_name=db_name)

	# if 'tabDefaultValue' not in frappe.db.get_tables():
	# 	import sys
	# 	from click import secho

	# 	secho(
	# 		"Table 'tabDefaultValue' missing in the restored site. "
	# 		"This may be due to incorrect permissions or the result of a restore from a bad backup file. "
	# 		"Database not installed correctly.",
	# 		fg="red"
	# 	)
	# 	sys.exit(1)

def import_db_from_sql(source_sql=None, verbose=False):
	db_file = frappe.get_site_path("private", "database.sqlite3")
	con = sqlite3.connect(db_file or ":memory:")
	cur = con.cursor()
	source_sql = source_sql or os.path.join(os.path.dirname(__file__), 'framework_sqlite.sql')
	cur.executescript(open(source_sql, "r").read())
	# print(cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())
	cur.close()
	con.commit()
	con.close()
