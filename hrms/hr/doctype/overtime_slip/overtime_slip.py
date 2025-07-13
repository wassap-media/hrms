# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import json
from datetime import timedelta
from email.utils import formatdate

import frappe
from frappe import _, bold
from frappe.model.docstatus import DocStatus
from frappe.model.document import Document
from frappe.utils import cstr, flt
from frappe.utils.data import format_time, get_link_to_form, getdate

from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	get_assigned_salary_structure,
)


class OvertimeSlip(Document):
	def validate(self):
		if not (self.start_date or self.end_date):
			self.get_frequency_and_dates()

		if self.start_date > self.end_date:
			frappe.throw(_("Start date cannot be greater than end date"))

		self.validate_overlap()
		self.validate_overtime_date_and_duration()

	def on_submit(self):
		self.process_overtime_slip()

	def validate_overlap(self):
		overtime_slips = frappe.db.get_all(
			"Overtime Slip",
			filters={
				"docstatus": ("<", 2),
				"employee": self.employee,
				"end_date": (">=", self.start_date),
				"start_date": ("<=", self.end_date),
				"name": ("!=", self.name),
			},
		)
		if len(overtime_slips):
			form_link = get_link_to_form("Overtime Slip", overtime_slips[0].name)
			msg = _("Overtime Slip:{0} has been created between {1} and {1}").format(
				bold(form_link), bold(self.start_date), bold(self.end_date)
			)
			frappe.throw(msg)

	def validate_overtime_date_and_duration(self):
		dates = set()
		overtime_type_cache = {}
		for detail in self.overtime_details:
			# check for duplicate dates
			if detail.date in dates:
				frappe.throw(_("Date {0} is repeated in Overtime Details").format(detail.date))
			dates.add(detail.date)

			# validate duration only for overtime details not linked to attendance
			if detail.reference_document:
				continue

			if detail.overtime_type not in overtime_type_cache:
				overtime_type_cache[detail.overtime_type] = frappe.db.get_value(
					"Overtime Type", detail.overtime_type, "maximum_overtime_hours_allowed"
				)
			maximum_overtime_hours = overtime_type_cache[detail.overtime_type]
			if maximum_overtime_hours:
				if detail.overtime_duration > maximum_overtime_hours:
					frappe.throw(
						_("Overtime Duration for {0} is greater than Maximum Overtime Hours Allowed").format(
							detail.date
						)
					)

	@frappe.whitelist()
	def get_frequency_and_dates(self):
		date = self.posting_date

		salary_structure = get_assigned_salary_structure(self.employee, date)
		if salary_structure:
			payroll_frequency = frappe.db.get_value("Salary Structure", salary_structure, "payroll_frequency")
			date_details = get_start_end_dates(
				payroll_frequency, date, frappe.db.get_value("Employee", self.employee, "company")
			)
			self.start_date = date_details.start_date
			self.end_date = date_details.end_date
		else:
			frappe.throw(
				_("Salary Structure not assigned for employee {0} for date {1}").format(
					self.employee, self.start_date
				)
			)

	@frappe.whitelist()
	def get_emp_and_overtime_details(self):
		records = self.get_attendance_records()
		if len(records):
			self.create_overtime_details_row_for_attendance(records)
		if len(self.overtime_details):
			total_overtime_duration = 0.0
			for detail in self.overtime_details:
				if detail.overtime_duration is not None:
					total_overtime_duration += detail.overtime_duration
			self.total_overtime_duration = total_overtime_duration
		self.save()

	def create_overtime_details_row_for_attendance(self, records):
		self.overtime_details = []
		overtime_type_cache = {}

		for record in records:
			if record.overtime_type not in overtime_type_cache:
				overtime_type_cache[record.overtime_type] = frappe.db.get_value(
					"Overtime Type", record.overtime_type, "maximum_overtime_hours_allowed"
				)

			maximum_overtime_hours_allowed = overtime_type_cache[record.overtime_type]
			overtime_duration = record.actual_overtime_duration or 0.0

			if maximum_overtime_hours_allowed > 0:
				overtime_duration = (
					overtime_duration
					if maximum_overtime_hours_allowed > overtime_duration
					else maximum_overtime_hours_allowed
				)

			if overtime_duration > 0:
				self.append(
					"overtime_details",
					{
						"reference_document": record.name,
						"date": record.attendance_date,
						"overtime_type": record.overtime_type,
						"overtime_duration": overtime_duration,
					},
				)

	def get_attendance_records(self):
		records = []
		if self.start_date and self.end_date:
			records = frappe.get_all(
				"Attendance",
				fields=[
					"name",
					"attendance_date",
					"overtime_type",
					"actual_overtime_duration",
				],
				filters={
					"employee": self.employee,
					"docstatus": 1,
					"attendance_date": ("between", [getdate(self.start_date), getdate(self.end_date)]),
					"status": "Present",
					"overtime_type": ["!=", ""],
				},
			)
			if not len(records):
				frappe.throw(
					_("No attendance records found for employee {0} between {1} and {2}").format(
						self.employee, self.start_date, self.end_date
					)
				)
		return records

	def process_overtime_slip(self):
		overtime_components = self.get_overtime_component_amounts()
		for component, total_amount in overtime_components.items():
			self.create_additional_salary(component, total_amount)

	def get_overtime_component_amounts(self):
		"""
		Get amount for each overtime detail child item, sum and group amounts by salary component for additional salary creation
		"""
		holiday_date_map = self.get_holiday_map()
		self.overtime_types = {}  # details of each overtime type
		overtime_components = {}  # store total amount against each overtime salary component

		for overtime_detail in self.overtime_details:
			overtime_type = overtime_detail.overtime_type

			self.get_overtime_types_with_details(overtime_type, overtime_detail.standard_working_hours)
			overtime_amount = self.calculate_overtime_amount(
				overtime_type, overtime_detail.overtime_duration, holiday_date_map
			)
			salary_component = self.overtime_types[overtime_type]["overtime_salary_component"]
			overtime_components[salary_component] = (
				overtime_components.get(salary_component, 0) + overtime_amount
			)

		return overtime_components

	def get_overtime_types_with_details(self, overtime_type, standard_working_hours):
		"""
		Get all configurations for an overtime type and set in self.overtime_types
		"""
		if overtime_type not in self.overtime_types:
			self.overtime_types[overtime_type] = self.get_overtime_type_details(overtime_type)
			self.overtime_types[overtime_type]["standard_working_hours"] = standard_working_hours
			self.overtime_types[overtime_type]["applicable_hourly_rate"] = self.get_applicable_hourly_rate(
				overtime_type
			)

	def calculate_overtime_amount(self, overtime_type, overtime_duration, holiday_date_map):
		"""
		Calculate total amount for the given overtime detail child item based on its type and date.
		"""

		overtime_details = self.overtime_types.get(overtime_type)
		if not overtime_details:
			return 0.0

		applicable_hourly_rate = overtime_details.get("applicable_hourly_rate", 0)
		overtime_date = cstr(overtime_details.get("date"))

		multiplier = overtime_details.get("standard_multiplier", 1)

		holiday_info = holiday_date_map.get(overtime_date)
		if holiday_info:
			if overtime_details.get("applicable_for_weekend") and holiday_info.weekly_off:
				multiplier = overtime_details.get("weekend_multiplier", multiplier)
			elif overtime_details.get("applicable_for_public_holiday") and not holiday_info.weekly_off:
				multiplier = overtime_details.get("public_holiday_multiplier", multiplier)

		amount = overtime_duration * applicable_hourly_rate * multiplier
		return amount

	def get_holiday_map(self):
		from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

		from hrms.utils.holiday_list import get_holiday_dates_between

		holiday_list = get_holiday_list_for_employee(self.employee)
		holiday_dates = get_holiday_dates_between(
			holiday_list, self.start_date, self.end_date, select_weekly_off=True, as_dict=True
		)

		holiday_date_map = {}
		for holiday_date in holiday_dates:
			holiday_date_map[cstr(holiday_date.holiday_date)] = holiday_date

		return holiday_date_map

	def get_overtime_type_details(self, name):
		details = frappe.get_value(
			"Overtime Type",
			filters={"name": name},
			fieldname=[
				"name",
				"standard_multiplier",
				"weekend_multiplier",
				"public_holiday_multiplier",
				"applicable_for_weekend",
				"applicable_for_public_holiday",
				"overtime_salary_component",
				"overtime_calculation_method",
				"hourly_rate",
			],
			as_dict=True,
		)

		components = []
		if details.overtime_calculation_method == "Salary Component Based":
			components = frappe.get_all(
				"Overtime Salary Component", filters={"parent": name}, fields=["salary_component"]
			)
			components = [data.salary_component for data in components]
		details["components"] = components

		return details

	def get_applicable_hourly_rate(self, overtime_type):
		overtime_details = self.overtime_types.get(overtime_type)
		overtime_calculation_method = overtime_details.get("overtime_calculation_method")

		applicable_hourly_rate = 0.0
		if overtime_calculation_method == "Fixed Hourly Rate":
			applicable_hourly_rate = overtime_details.get("hourly_rate", 0.0)
		elif overtime_calculation_method == "Salary Component Based":
			applicable_hourly_rate = self.get_hourly_rate_for_overtime_based_on_salary_component(
				overtime_type
			)
		return applicable_hourly_rate

	def get_hourly_rate_for_overtime_based_on_salary_component(self, overtime_type):
		from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip

		components = self.overtime_types[overtime_type]["components"]
		salary_structure = get_assigned_salary_structure(self.employee, self.start_date)

		if not hasattr(self, "_cached_salary_slip"):
			self._cached_salary_slip = make_salary_slip(
				salary_structure,
				employee=self.employee,
				ignore_permissions=True,
				posting_date=self.start_date,
			)

		component_amount = sum(
			[
				data.amount
				for data in self._cached_salary_slip.earnings
				if data.salary_component in components and not data.get("additional_salary", None)
			]
		)

		standard_working_hours = self.overtime_types[overtime_type]["standard_working_hours"]
		applicable_daily_amount = component_amount / self._cached_salary_slip.payment_days
		return applicable_daily_amount / standard_working_hours

	def create_additional_salary(self, salary_component, total_amount):
		if total_amount > 0:
			precision = frappe.db.get_single_value("System Settings", "currency_precision") or 2
			additional_salary = frappe.get_doc(
				{
					"doctype": "Additional Salary",
					"company": self.company,
					"employee": self.employee,
					"salary_component": salary_component,
					"amount": flt(total_amount, precision),
					"payroll_date": self.start_date,
					"overwrite_salary_structure_amount": 0,
					"ref_doctype": "Overtime Slip",
					"ref_docname": self.name,
				}
			)
			additional_salary.save()
			additional_salary.submit()


@frappe.whitelist()
def filter_employees_for_overtime_slip_creation(start_date, end_date, employees):
	if not employees:
		return []

	if not isinstance(employees, list):
		employees = json.loads(employees)

	OvertimeSlip = frappe.qb.DocType("Overtime Slip")
	Attendance = frappe.qb.DocType("Attendance")

	# Employees with existing Overtime Slips in the date range
	employees_with_overtime_slips = (
		frappe.qb.from_(OvertimeSlip)
		.select(OvertimeSlip.employee)
		.where(
			(OvertimeSlip.docstatus != 2)
			& (OvertimeSlip.start_date <= end_date)
			& (OvertimeSlip.end_date >= start_date)
			& (OvertimeSlip.employee.isin(employees))
		)
	).run(pluck=True)

	# Employees who have attendance records with non-empty overtime_type
	employees_with_valid_attendance = (
		frappe.qb.from_(Attendance)
		.select(Attendance.employee)
		.where(
			(Attendance.employee.isin(employees))
			& (Attendance.attendance_date >= start_date)
			& (Attendance.attendance_date <= end_date)
			& (Attendance.overtime_type != "")
		)
		.distinct()
	).run(pluck=True)

	# employees with valid attendance AND no overtime slips
	eligible_employees = set(employees_with_valid_attendance) - set(employees_with_overtime_slips)

	return eligible_employees


def create_overtime_slips_for_employees(employees, args):
	count = 0
	errors = []
	for emp in employees:
		args.update({"doctype": "Overtime Slip", "employee": emp})
		try:
			doc = frappe.get_doc(args)
			doc.get_emp_and_overtime_details()
			count += 1
		except Exception as e:
			frappe.clear_last_message()
			frappe.db.rollback()
			errors.append(_("Employee {0} : {1}").format(emp, str(e)))
			frappe.log_error(frappe.get_traceback(), _("Overtime Slip Creation Error for {0}").format(emp))
	if count:
		frappe.msgprint(
			_("Overtime Slip created for {0} employee(s)").format(count),
			indicator="green",
			title=_("Overtime Slips Created"),
		)
	if errors:
		error_list_html = "".join(f"<li>{err}</li>" for err in errors)
		frappe.msgprint(
			title=_("Overtime Slip Creation Failed"),
			msg=f"<ul>{error_list_html}</ul>",
			indicator="red",
		)

	frappe.publish_realtime("completed_overtime_slip_creation", user=frappe.session.user)


def submit_overtime_slips_for_employees(overtime_slips):
	count = 0
	errors = []
	for overtime_slip in overtime_slips:
		try:
			doc = frappe.get_doc("Overtime Slip", overtime_slip)
			doc.submitted_via_payroll_entry = 1
			doc.submit()
			count += 1
		except Exception as e:
			frappe.clear_last_message()
			frappe.db.rollback()
			errors.append(_("{0} : {1}").format(overtime_slip, str(e)))
			frappe.log_error(
				frappe.get_traceback(), _("Overtime Slip Submission Error for {0}").format(overtime_slip)
			)
	if count:
		frappe.msgprint(
			_("Overtime Slips submitted for {0} employee(s)").format(count),
			indicator="green",
			title=_("Overtime Slip Submitted"),
		)
	if errors:
		error_list_html = "".join(f"<li>{err}</li>" for err in errors)
		frappe.msgprint(
			title=_("Overtime Slip Submission Failed"),
			msg=_(f"<ul>{error_list_html}</ul>"),
			indicator="red",
		)

	frappe.publish_realtime("completed_overtime_slip_submission", user=frappe.session.user)
