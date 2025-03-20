# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

# import frappe
from datetime import timedelta

import frappe
from frappe.tests import UnitTestCase
from frappe.utils import flt
from frappe.utils.data import add_days, get_datetime, get_first_day, nowdate, today

from erpnext.setup.doctype.employee.test_employee import make_employee

from hrms.hr.doctype.employee_checkin.test_employee_checkin import make_checkin
from hrms.hr.doctype.overtime_type.test_overtime_type import create_overtime_type
from hrms.hr.doctype.shift_type.test_shift_type import make_shift_assignment, setup_shift_type
from hrms.payroll.doctype.salary_slip.test_salary_slip import clear_cache
from hrms.payroll.doctype.salary_structure.test_salary_structure import (
	make_salary_structure,
)

# On IntegrationTestCase, the doctype test records and all
# link-field test record depdendencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class TestOvertimeSlip(UnitTestCase):
	def setUp(self):
		for doctype in [
			"Overtime Type",
			"Overtime Slip",
			"Attendance",
			"Employee Checkin",
			"Shift Type",
			"Shift Assignment",
		]:
			frappe.db.sql(f"DELETE FROM `tab{doctype}`")
		clear_cache()

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

	def test_overtime_calculation_and_additional_salary_creation(self):
		from hrms.hr.doctype.overtime_slip.overtime_slip import convert_str_time_to_hours
		from hrms.hr.doctype.overtime_type.test_overtime_type import create_overtime_type
		from hrms.hr.doctype.shift_type.test_shift_type import setup_shift_type
		from hrms.payroll.doctype.salary_slip.test_salary_slip import make_salary_component
		from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip
		from hrms.payroll.doctype.salary_structure.test_salary_structure import make_salary_structure

		setup_shift_type(company="_Test Company")

		employee = make_employee("test_overtime_slip@example.com")
		salary_structure = make_salary_structure(
			"Test Overtime Salary Slip",
			"Monthly",
			employee=employee,
			company="_Test Company",
		)

		component = [
			{
				"salary_component": "Overtime Allowance",
				"abbr": "OA",
				"type": "Earning",
				"amount_based_on_formula": 0,
			}
		]
		make_salary_component(component, test_tax=0, company_list=["_Test Company"])

		overtime_type = create_overtime_type(employee=employee)
		attendance = create_attendance_records_for_overtime(employee, overtime_type=overtime_type.name)

		salary_slip = make_salary_slip(salary_structure.name, employee=employee)

		total_overtime_hours = 0
		for attendance_entry in attendance.values():
			total_overtime_hours += convert_str_time_to_hours(attendance_entry["overtime_duration"])

		slip = create_overtime_slip(employee)
		slip.status = "Approved"
		slip.submit()

		overtime_component_details = {}
		applicable_amount = 0

		for earning in salary_slip.earnings:
			if earning.salary_component == "Basic Salary":
				applicable_amount = earning.default_amount

		additional_salary_amount = frappe.db.get_value(
			"Additional Salary", {"ref_docname": slip.name}, "amount"
		)

		self.assertIn("Overtime Allowance", overtime_component_details.salary_component)
		self.assertEqual(slip.name, overtime_component_details.overtime_slips)

		daily_wages = applicable_amount / salary_slip.total_working_days
		hourly_wages = daily_wages / 4

		overtime_amount = hourly_wages * total_overtime_hours * overtime_type.standard_multiplier

		self.assertEqual(flt(overtime_amount, 2), flt(additional_salary_amount.amount, 2))


def create_overtime_slip(employee):
	slip = frappe.new_doc("Overtime Slip")
	slip.employee = employee
	slip.posting_date = today()
	slip.overtime_details = []

	slip.save()
	return slip


def create_attendance_records_for_overtime(employee, overtime_type):
	records = {}
	for x in range(2):
		attendance = frappe.new_doc("Attendance")
		attendance.employee = employee
		attendance.status = "Present"
		attendance.attendance_date = add_days(today(), -(x))
		attendance.overtime_type = overtime_type
		attendance.overtime_duration = "02:00:00"
		attendance.standard_working_hours = timedelta(hours=4)

		attendance.save()
		attendance.submit()

		records[attendance.name] = {
			"overtime_duration": attendance.overtime_duration,
			"overtime_type": attendance.overtime_type,
			"attendance_date": attendance.attendance_date,
		}

	return records
