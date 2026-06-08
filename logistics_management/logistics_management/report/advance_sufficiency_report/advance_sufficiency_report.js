// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Advance Sufficiency Report"] = {
	filters: [
		{
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date"
        },

        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date"
        },

        {
            fieldname: "driver",
            label: "Driver",
            fieldtype: "Link",
            options: "Employee"
        }
	],
};
