frappe.query_reports["Advance Sufficiency Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": "From Date",
			"fieldtype": "Date"
		},
		{
			"fieldname": "to_date",
			"label": "To Date",
			"fieldtype": "Date"
		},
		{
			"fieldname": "driver",
			"label": "Driver",
			"fieldtype": "Link",
			"options": "Employee"
		}
	]
};