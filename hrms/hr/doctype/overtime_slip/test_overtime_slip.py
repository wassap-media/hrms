# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

# import frappe
from datetime import timedelta

import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase
from frappe.utils.data import get_datetime, get_first_day, nowdate, today

from erpnext.setup.doctype.employee.test_employee import make_employee

from hrms.hr.doctype.employee_checkin.test_employee_checkin import make_checkin
from hrms.hr.doctype.overtime_type.test_overtime_type import create_overtime_type
from hrms.hr.doctype.shift_type.test_shift_type import make_shift_assignment, setup_shift_type
from hrms.payroll.doctype.salary_structure.test_salary_structure import (
	make_salary_structure,
)

# On IntegrationTestCase, the doctype test records and all
# link-field test record depdendencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class TestOvertimeSlip(UnitTestCase):
	def test_create_overtime_slip(self):
		if not frappe.db.exists("Company", "_Test Company"):
			company = frappe.new_doc("Company")
			company.company_name = "_Test Company"
			company.abbr = "_TC"
			company.default_currency = "INR"
			company.country = "India"
			company.insert()

		shift_type = setup_shift_type()

		employee = make_employee("test_overtime_slipn@example.com", company="_Test Company")
		overtime_type = create_overtime_type(employee=employee)

		shift_type.allow_overtime = 1
		shift_type.overtime_type = overtime_type.name
		shift_type.save()

		make_shift_assignment(shift_type.name, employee, get_first_day(nowdate()))
		make_salary_structure(
			"Test Overtime Salary Slip",
			"Monthly",
			employee=employee,
			company="_Test Company",
		)
		frappe.db.set_value("Employee", employee, "default_shift", shift_type.name)

		checkin = make_checkin(employee, time=get_datetime(today()) + timedelta(hours=8), log_type="IN")
		checkout = make_checkin(employee, time=get_datetime(today()) + timedelta(hours=13), log_type="OUT")
		self.assertEqual(checkin.shift, shift_type.name)
		self.assertEqual(checkout.shift, shift_type.name)

		shift_type.reload()
		shift_type.process_auto_attendance()
		checkin.reload()

		attendance_records = frappe.get_all(
			"Attendance",
			filters={"shift": shift_type.name, "status": "Present"},
			fields=["name", "overtime_duration", "overtime_type", "attendance_date"],
		)

		records = {}
		for record in attendance_records:
			records[record.name] = {
				"overtime_duration": record.overtime_duration,
				"overtime_type": record.overtime_type,
				"attendance_date": record.attendance_date,
			}

		slip = create_overtime_slip(employee)

		for detail in slip.overtime_details:
			self.assertIn(detail.reference_document, records.keys())
			if detail.reference_document in records.keys():
				self.assertEqual(
					detail.overtime_duration, records[detail.reference_document]["overtime_duration"]
				)
				self.assertEqual(str(detail.date), str(records[detail.reference_document]["attendance_date"]))

	def tearDown(self):
		for doctype in [
			"Overtime Type",
			"Overtime Slip",
			"Attendance",
			"Employee Checkin",
			"Shift Type",
			"Shift Assignment",
		]:
			frappe.db.sql(f"DELETE FROM `tab{doctype}`")
		frappe.db.commit()


def create_overtime_slip(employee):
	slip = frappe.new_doc("Overtime Slip")
	slip.employee = employee
	slip.posting_date = today()
	slip.overtime_details = []

	slip.save()
	return slip
