import frappe

if frappe._asgi_server:
	from starlette.responses import Response
	from starlette.requests import Request
else:
	from werkzeug.wrappers import Response, Request
