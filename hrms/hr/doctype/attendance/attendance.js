// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.ui.form.on("Attendance", {
	refresh(frm) {
		if (frm.doc.__islocal && !frm.doc.attendance_date) {
			frm.set_value("attendance_date", frappe.datetime.get_today());
		}

		frm.set_query("employee", () => {
			return {
				query: "erpnext.controllers.queries.employee_query",
			};
		});
	},
	employee: function (frm) {
		if (frm.doc.employee && frm.doc.attendance_date) {
			frm.events.set_shift(frm);
		}
	},
	set_shift: function (frm) {
		frappe.call({
			method: "hrms.hr.doctype.attendance.attendance.get_shift_type",
			args: {
				employee: frm.doc.employee,
				attendance_date: frm.doc.attendance_date,
			},
			callback: function (r) {
				if (r.message) {
					frm.set_value("shift", r.message);
				}
			},
		});
	},
});
