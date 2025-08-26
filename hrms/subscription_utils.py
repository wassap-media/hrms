import requests

import frappe

STANDARD_ROLES = [
	# standard roles
	"Administrator",
	"All",
	"Guest",
	# accounts
	"Accounts Manager",
	"Accounts User",
	# projects
	"Projects User",
	"Projects Manager",
	# framework
	"Blogger",
	"Dashboard Manager",
	"Inbox User",
	"Newsletter Manager",
	"Prepared Report User",
	"Report Manager",
	"Script Manager",
	"System Manager",
	"Website Manager",
	"Workspace Manager",
]


@frappe.whitelist(allow_guest=True)
def get_add_on_details(plan: str) -> dict[str, int]:
	"""
	Returns the number of employees to be billed under add-ons for SAAS subscription
	site_details = {
	        "country": "India",
	        "plan": "Basic",
	        "credit_balance": 1000,
	        "add_ons": {
	                "employee": 2,
	        },
	        "expiry_date": "2021-01-01", # as per current usage
	}
	"""
	EMPLOYEE_LIMITS = {"Basic": 25, "Essential": 50, "Professional": 100}
	add_on_details = {}

	employees_included_in_plan = EMPLOYEE_LIMITS.get(plan)
	if employees_included_in_plan:
		active_employees = get_active_employees()
		add_on_employees = (
			active_employees - employees_included_in_plan
			if active_employees > employees_included_in_plan
			else 0
		)
	else:
		add_on_employees = 0

	add_on_details["employees"] = add_on_employees
	return add_on_details


def get_active_employees() -> int:
	return frappe.db.count("Employee", {"status": "Active"})


@frappe.whitelist(allow_guest=True)
def subscription_updated(app: str, plan: str):
	if app in ["hrms", "erpnext"] and plan:
		update_erpnext_access()


def update_erpnext_access(user_input: dict | None):
	"""
	Called from hooks after setup wizard completion, ignored if user has no hrms subscription
	enables erpnext workspaces and roles if user has subscribed to both hrms and erpnext
	disables erpnext workspaces and roles if user has subscribed to hrms but not erpnext
	"""
	if not frappe.utils.get_url().endswith(".frappehr.com"):
		return

	update_erpnext_workspaces(True)
	update_erpnext_roles(True)
	set_app_logo()


def update_erpnext_workspaces(disable: bool = True):
	erpnext_workspaces = [
		"Home",
		"Assets",
		"Accounting",
		"Buying",
		"CRM",
		"Manufacturing",
		"Quality",
		"Selling",
		"Stock",
		"Support",
	]

	for workspace in erpnext_workspaces:
		try:
			workspace_doc = frappe.get_doc("Workspace", workspace)
			workspace_doc.flags.ignore_links = True
			workspace_doc.flags.ignore_validate = True
			workspace_doc.public = 0 if disable else 1
			workspace_doc.save()
		except Exception:
			frappe.clear_messages()


def update_erpnext_roles(disable: bool = True):
	roles = get_erpnext_roles()
	for role in roles:
		try:
			role_doc = frappe.get_doc("Role", role)
			role_doc.disabled = disable
			role_doc.flags.ignore_links = True
			role_doc.save()
		except Exception:
			pass


def set_app_logo():
	# Logo removed - no longer setting app logo
	pass


# ERPNext functions removed - no longer needed
# def update_erpnext_workspaces(disable: bool = True):
# def update_erpnext_roles(disable: bool = True):
# def get_erpnext_roles() -> set:
# def get_roles_for_app(app_name: str) -> set:
# def get_modules_by_app(app_name: str) -> list:
# def get_doctypes_by_modules(modules: list) -> list:
# def roles_by_doctype(doctypes: list) -> set:
# def hide_erpnext() -> bool:
# def has_subscription(secret_key) -> bool:
