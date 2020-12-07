import frappe
import json
import os


def get_context(context):
    def get_size(size):
        if size > 1048576:
            return "{0:.1f}M".format(float(size) / 1048576)
        else:
            return "{0:.1f}K".format(float(size) / 1024)

    logs = {
        x: get_size(y)
        for x, y
        in sorted(
            frappe.site_logs().items(),
            key=lambda x: os.path.getmtime(os.path.join(frappe.local.site, "logs", x[0])),
            reverse=True
        )
    }

    return {"logs": json.dumps(logs), **context}
