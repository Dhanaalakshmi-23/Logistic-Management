# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _



def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [

        {
            "label": "Trip",
            "fieldname": "trip",
            "fieldtype": "Link",
            "options": "Transport Trip",
            "width": 150
        },

        {
            "label": "Trip Date",
            "fieldname": "trip_date",
            "fieldtype": "Date",
            "width": 120
        },

        {
            "label": "Driver",
            "fieldname": "driver",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 150
        },

        {
            "label": "Driver Name",
            "fieldname": "driver_name",
            "fieldtype": "Data",
            "width": 180
        },

        {
            "label": "Advance Given",
            "fieldname": "advance_given",
            "fieldtype": "Currency",
            "width": 130
        },

        {
            "label": "Actual Expense",
            "fieldname": "actual_expense",
            "fieldtype": "Currency",
            "width": 130
        },

        {
            "label": "Difference",
            "fieldname": "difference",
            "fieldtype": "Currency",
            "width": 130
        },

        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 180
        }

    ]

def get_conditions(filters):

    conditions = ""

    if not filters:
        return conditions

    if filters.get("driver"):
        conditions += " AND driver = %(driver)s"

    if filters.get("from_date"):
        conditions += " AND trip_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND trip_date <= %(to_date)s"

    return conditions


def get_data(filters):

    conditions = get_conditions(filters)

    data = frappe.db.sql(
        f"""
        select
            name as trip,
            trip_date,
            driver,
            driver_name,
            advance_given_to_driver as advance_given,
            total_expense as actual_expense

        from `tabTransport Trip`

        where
            docstatus = 1
            {conditions}

        order by trip_date desc
        """,
        filters,
        as_dict=True
    )

    for row in data:

        advance = row.advance_given or 0
        expense = row.actual_expense or 0

        row.difference = advance - expense

        if row.difference > 500:

            row.status = """
			<span style="color:green;font-weight:bold;">
				Well Planned
			</span>
			"""

        elif row.difference >= 0:

            row.status = """
			<span style="color:orange;font-weight:bold;">
				Exact Match
			</span>
			"""

        else:

            row.status = """
			<span style="color:red;font-weight:bold;">
				Extra Payment Needed
			</span>
			"""

    return data
