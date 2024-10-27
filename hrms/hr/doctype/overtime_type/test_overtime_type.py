# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

# import frappe
import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase

import erpnext

from hrms.payroll.doctype.salary_slip.test_salary_slip import make_salary_component

# On IntegrationTestCase, the doctype test records and all
# link-field test record depdendencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class TestOvertimeType(UnitTestCase):
	"""
	Unit tests for OvertimeType.
	Use this class for testing individual functions and methods.
	"""

	pass


def create_overtime_type(**args):
	args = frappe._dict(args)
	overtime_type = frappe.new_doc("Overtime Type")
	overtime_type.name = "_Test Overtime"

	overtime_type.standard_multiplier = 1.25
	overtime_type.applicable_for_weekend = args.applicable_for_weekend or 0
	overtime_type.applicable_for_public_holiday = args.applicable_for_public_holiday or 0
	overtime_type.maximum_overtime_hours_allowed = args.maximum_overtime_hours_allowed or 0
	overtime_type.overtime_salary_component = args.overtime_salary_component or "Overtime Allowance"

	if args.applicable_for_weekend:
		overtime_type.weekend_multiplier = 1.5

	if args.applicable_for_public_holidays:
		overtime_type.public_holiday_multiplier = 2

	component = [
		{
			"salary_component": "Basic Salary",
			"abbr": "BA",
			"type": "Earning",
		},
		{
			"salary_component": "Overtime Allowance",
			"abbr": "OA",
			"type": "Earning",
		},
	]

	company = erpnext.get_default_company()
	make_salary_component(component, test_tax=0, company_list=[company])
	overtime_type.append("applicable_salary_component", {"salary_component": "Basic Salary"})

	overtime_type.insert(ignore_if_duplicate=True)

	return overtime_type
