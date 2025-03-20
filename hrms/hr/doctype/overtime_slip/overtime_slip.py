# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from datetime import timedelta
from email.utils import formatdate

import frappe
from frappe import _, bold
from frappe.model.docstatus import DocStatus
from frappe.model.document import Document
from frappe.utils import cstr
from frappe.utils.data import format_time, get_link_to_form, getdate

from hrms.payroll.doctype.payroll_entry.payroll_entry import get_start_end_dates
from hrms.payroll.doctype.salary_structure_assignment.salary_structure_assignment import (
	get_assigned_salary_structure,
)


class OvertimeSlip(Document):
	def validate(self):
		if not (self.from_date or self.to_date or self.payroll_frequency):
			self.get_frequency_and_dates()

		self.validate_overlap()
		if self.from_date >= self.to_date:
			frappe.throw(_("From date can not be greater than To date"))

		if not len(self.overtime_details):
			self.get_emp_and_overtime_details()

	def validate_overlap(self):
		overtime_slips = frappe.db.get_all(
			"Overtime Slip",
			filters={
				"docstatus": ("<", 2),
				"employee": self.employee,
				"to_date": (">=", self.from_date),
				"from_date": ("<=", self.to_date),
				"name": ("!=", self.name),
			},
		)
		if len(overtime_slips):
			form_link = get_link_to_form("Overtime Slip", overtime_slips[0].name)
			msg = _("Overtime Slip:{0} has been created between {1} and {1}").format(
				bold(form_link), bold(self.from_date), bold(self.to_date)
			)
			frappe.throw(msg)

	def on_submit(self):
		if self.status == "Pending":
			frappe.throw(_("Overtime Slip with Status 'Approved' or 'Rejected' are allowed for Submission"))

		if self.status == "Approved":
			self.process_overtime_slip()

	@frappe.whitelist()
	def get_frequency_and_dates(self):
		date = self.from_date or self.posting_date

		salary_structure = get_assigned_salary_structure(self.employee, date)
		if salary_structure:
			payroll_frequency = frappe.db.get_value("Salary Structure", salary_structure, "payroll_frequency")
			date_details = get_start_end_dates(
				payroll_frequency, date, frappe.db.get_value("Employee", self.employee, "company")
			)
			self.from_date = date_details.start_date
			self.to_date = date_details.end_date
			self.payroll_frequency = payroll_frequency
		else:
			frappe.throw(_("No Salary Structure Assignment found for Employee: {0}").format(self.employee))

	@frappe.whitelist()
	def get_emp_and_overtime_details(self):
		records = self.get_attendance_record()
		if len(records):
			self.create_overtime_details_row_for_attendance(records)
		if len(self.overtime_details):
			self.total_overtime_duration = timedelta()
			for detail in self.overtime_details:
				if detail.overtime_duration is not None:
					self.total_overtime_duration += detail.overtime_duration

	def create_overtime_details_row_for_attendance(self, records):
		self.overtime_details = []
		for record in records:
			if record.overtime_duration:
				self.append(
					"overtime_details",
					{
						"reference_document_type": "Attendance",
						"reference_document": record.name,
						"date": record.attendance_date,
						"overtime_type": record.overtime_type,
						"overtime_duration": record.overtime_duration,
						"standard_working_hours": record.standard_working_hours,
					},
				)

	def get_attendance_record(self):
		records = []
		if self.from_date and self.to_date:
			records = frappe.get_all(
				"Attendance",
				fields=[
					"overtime_duration",
					"name",
					"attendance_date",
					"overtime_type",
					"standard_working_hours",
				],
				filters={
					"employee": self.employee,
					"docstatus": DocStatus.submitted(),
					"attendance_date": ("between", [getdate(self.from_date), getdate(self.to_date)]),
					"status": "Present",
					"overtime_type": ["!=", ""],
				},
			)
		return records

	def create_additional_salary(self, salary_component, total_amount):
		if total_amount > 0:
			additional_salary = frappe.get_doc(
				{
					"doctype": "Additional Salary",
					"company": self.company,
					"employee": self.employee,
					"salary_component": salary_component,
					"amount": total_amount,
					"payroll_date": self.from_date,
					"overwrite_salary_structure_amount": 0,
					"ref_doctype": "Overtime Slip",
					"ref_docname": self.name,
				}
			)
			additional_salary.save()
			additional_salary.submit()

	def process_overtime_slip(self):
		overtime_components = self.get_overtime_component_amounts()
		for component, total_amount in overtime_components.items():
			self.create_additional_salary(component, total_amount)

	def get_overtime_component_amounts(self):
		"""
		Calculate total amount for each salary component based on overtime details
		"""
		holiday_date_map = self.get_holiday_map()
		overtime_types = {}
		overtime_components = {}

		for overtime_detail in self.overtime_details:
			overtime_type = overtime_detail.overtime_type
			overtime_types = self.set_overtime_type_details(overtime_types, overtime_detail)
			overtime_amounts = self.calculate_overtime_amount(
				overtime_types, overtime_detail, holiday_date_map
			)
			salary_component = overtime_types[overtime_type]["overtime_salary_component"]

			overtime_components[salary_component] = overtime_components.get(salary_component, 0) + sum(
				overtime_amounts
			)

		return overtime_components

	def set_overtime_type_details(self, overtime_types, overtime_type_details):
		"""
		Store details of each overtime type in overtime_types
		"""
		overtime_type = overtime_type_details.overtime_type
		if overtime_type not in overtime_types:
			details = self.get_overtime_type_details(overtime_type)
			overtime_types[overtime_type] = details

			overtime_types[overtime_type]["standard_working_hours"] = (
				overtime_type_details.standard_working_hours
			)
			overtime_types[overtime_type]["overtime_duration"] = overtime_type_details.overtime_duration

			if "applicable_hourly_rate" not in overtime_types[overtime_type]:
				self.set_applicable_hourly_rate(overtime_types, overtime_type)

		return overtime_types

	def calculate_overtime_amount(self, overtime_types, overtime_detail, holiday_date_map):
		"""
		Calculate total amount
		"""
		standard_duration_amount, weekends_duration_amount = 0, 0
		public_holidays_duration_amount, calculated_amount = 0, 0
		overtime_hours = convert_str_time_to_hours(overtime_detail.overtime_duration)

		applicable_hourly_rate = overtime_types[overtime_detail.overtime_type]["applicable_hourly_rate"]

		weekend_multiplier, public_holiday_multiplier = self.get_multipliers(
			overtime_types, overtime_detail.overtime_type
		)
		overtime_date = cstr(overtime_detail.date)
		if overtime_date in holiday_date_map.keys():
			if holiday_date_map[overtime_date].weekly_off == 1:
				calculated_amount = overtime_hours * applicable_hourly_rate * weekend_multiplier
				weekends_duration_amount += calculated_amount
			elif holiday_date_map[overtime_date].weekly_off == 0:
				calculated_amount = overtime_hours * applicable_hourly_rate * public_holiday_multiplier
				public_holidays_duration_amount += calculated_amount
		else:
			calculated_amount = (
				overtime_hours
				* applicable_hourly_rate
				* overtime_types[overtime_detail.overtime_type]["standard_multiplier"]
			)
			standard_duration_amount += calculated_amount

		return weekends_duration_amount, public_holidays_duration_amount, standard_duration_amount

	def get_multipliers(self, overtime_types, overtime_type):
		weekend_multiplier = overtime_types[overtime_type]["standard_multiplier"]
		public_holiday_multiplier = overtime_types[overtime_type]["standard_multiplier"]

		if overtime_types[overtime_type]["applicable_for_weekend"]:
			weekend_multiplier = overtime_types[overtime_type]["weekend_multiplier"]
		if overtime_types[overtime_type]["applicable_for_public_holiday"]:
			public_holiday_multiplier = overtime_types[overtime_type]["public_holiday_multiplier"]

		return weekend_multiplier, public_holiday_multiplier

	def get_holiday_map(self):
		from erpnext.setup.doctype.employee.employee import get_holiday_list_for_employee

		from hrms.utils.holiday_list import get_holiday_dates_between

		holiday_list = get_holiday_list_for_employee(self.employee)
		holiday_dates = get_holiday_dates_between(holiday_list, self.from_date, self.to_date, as_dict=True)

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
			self.validate_applicable_components(components, name)

		details["components"] = components

		return details

	def validate_applicable_components(self, applicable_components, overtime_type):
		if not len(applicable_components):
			frappe.throw(
				_("Select applicable components in Overtime Type: {0}").format(frappe.bold(overtime_type))
			)

	def set_applicable_hourly_rate(self, overtime_types, overtime_type):
		overtime_type_details = overtime_types[overtime_type]
		if overtime_type_details["overtime_calculation_method"] == "Fixed Hourly Rate":
			overtime_types[overtime_type]["applicable_hourly_rate"] = overtime_type_details.hourly_rate
			return
		self.get_hourly_rate_for_overtime_based_on_salary_component(overtime_types, overtime_type)

	def get_hourly_rate_for_overtime_based_on_salary_component(self, overtime_types, overtime_type):
		from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip

		overtime_type_details = overtime_types[overtime_type]
		components = overtime_type_details["components"]
		salary_structure = get_assigned_salary_structure(self.employee, self.from_date)

		if not hasattr(self, "_cached_salary_slip"):
			self._cached_salary_slip = make_salary_slip(
				salary_structure,
				employee=self.employee,
				ignore_permissions=True,
				posting_date=self.from_date,
			)

		component_amount = sum(
			[
				data.default_amount
				for data in self._cached_salary_slip.earnings
				if data.salary_component in components and not data.get("additional_salary", None)
			]
		)

		standard_working_hours = convert_str_time_to_hours(overtime_type_details.standard_working_hours)
		applicable_daily_amount = component_amount / self._cached_salary_slip.payment_days
		overtime_type_details["applicable_hourly_rate"] = applicable_daily_amount / standard_working_hours


def convert_str_time_to_hours(duration_str):
	# Split the string into hours, minutes, and seconds
	if isinstance(duration_str, timedelta):
		duration_str = format_time(duration_str)
	if not duration_str:
		return
	parts = duration_str.split(":")
	hours = int(parts[0])
	minutes = int(parts[1]) if len(parts) > 1 else 0
	seconds = int(float(parts[2])) if len(parts) > 2 else 0  # Default to 0 if seconds are missing

	total_seconds = hours * 3600 + minutes * 60 + seconds
	return total_seconds / 3600
