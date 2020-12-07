frappe.pages["logs"].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		single_column: true
	});
	$(
		frappe.render_template("logs")
	).appendTo(
		page.body.addClass("no-border")
	);
};
