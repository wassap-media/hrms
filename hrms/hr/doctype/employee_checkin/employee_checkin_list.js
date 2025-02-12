frappe.listview_settings["Employee Checkin"] = {
	add_fields: ["is_invalid"],
	get_indicator: function (doc) {
		if (doc.is_invalid) {
			return [__("Invalid"), "red", "is_invalid,=,1"];
		}
	},
	onload: function (listview) {
		listview.page.add_action_item(__("Fetch Shifts"), () => {
			const checkins = listview.get_checked_items().map((checkin) => checkin.name);
			frappe.call({
				method: "hrms.hr.doctype.employee_checkin.employee_checkin.bulk_fetch_shift",
				freeze: true,
				args: {
					checkins,
				},
			});
		});
	},
};
