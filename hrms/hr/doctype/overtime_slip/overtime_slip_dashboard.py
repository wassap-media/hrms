def get_data():
	return {
		"fieldname": "reference_name",
		"non_standard_fieldnames": {
			"Additional Salary": "ref_docname",
		},
		"transactions": [{"label": ("Payment"), "items": ["Additional Salary"]}],
	}
