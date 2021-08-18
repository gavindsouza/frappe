import frappe

if frappe._asgi_server:
	from starlette.exceptions import HTTPException
else:
	from werkzeug.exceptions import HTTPException

class NotFound(HTTPException):
	"""*404* `Not Found`

	Raise if a resource does not exist and never existed.
	"""

	code = 404
	description = (
		"The requested URL was not found on the server. If you entered"
		" the URL manually please check your spelling and try again."
	)

class Forbidden(HTTPException):
	"""*403* `Forbidden`

	Raise if the user doesn't have the permission for the requested resource
	but was authenticated.
	"""

	code = 403
	description = (
		"You don't have the permission to access the requested"
		" resource. It is either read-protected or not readable by the"
		" server."
	)
