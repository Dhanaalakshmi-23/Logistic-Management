# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
import frappe
from frappe import _


def execute(filters=None):

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)

    return columns, data, None, chart, summary

def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	return [

        {
            "label": "Expense Category",
            "fieldname": "expense_category",
            "fieldtype": "Link",
            "options": "Driver Expense Category",
            "width": 200
        },

        {
            "label": "Expense Type",
            "fieldname": "expense_type",
            "fieldtype": "Data",
            "width": 150
        },

        {
            "label": "Total Amount",
            "fieldname": "total_amount",
            "fieldtype": "Currency",
            "width": 150
        },

        {
            "label": "Percentage",
            "fieldname": "percentage",
            "fieldtype": "Percent",
            "width": 120
        },

        {
            "label": "Cost Level",
            "fieldname": "cost_level",
            "fieldtype": "HTML",
            "width": 180
        }

    ]


def get_conditions(filters):

    conditions = ""

    if not filters:
        return conditions

    if filters.get("driver"):
        conditions += " AND de.driver = %(driver)s"

    if filters.get("from_date"):
        conditions += " AND de.posting_date >= %(from_date)s"

    if filters.get("to_date"):
        conditions += " AND de.posting_date <= %(to_date)s"

    return conditions


def get_data(filters):

    conditions = get_conditions(filters)

    data = frappe.db.sql(
        f"""
        SELECT

            ded.expense_category,
            ded.expense_type,
            SUM(ded.amount) as total_amount

        FROM `tabDriver Expense Entry` de

        INNER JOIN `tabDriver Expense Detail` ded
            ON ded.parent = de.name

        WHERE
            de.docstatus = 1
            {conditions}

        GROUP BY ded.expense_category

        ORDER BY total_amount DESC
        """,
        filters,
        as_dict=True
    )

    grand_total = 0

    for row in data:
        grand_total += row.total_amount or 0

    for row in data:

        if grand_total > 0:

            row.percentage = round(
                (row.total_amount / grand_total) * 100,
                2
            )

        else:
            row.percentage = 0

        if row.percentage >= 50:

            row.cost_level = """
            <span style="
                background:#f8d7da;
                color:#721c24;
                padding:4px 8px;
                border-radius:10px;
                font-weight:bold;
            ">
            High Cost
            </span>
            """

        elif row.percentage >= 20:

            row.cost_level = """
            <span style="
                background:#fff3cd;
                color:#856404;
                padding:4px 8px;
                border-radius:10px;
                font-weight:bold;
            ">
            Medium Cost
            </span>
            """

        else:

            row.cost_level = """
            <span style="
                background:#d4edda;
                color:#155724;
                padding:4px 8px;
                border-radius:10px;
                font-weight:bold;
            ">
            Low Cost
            </span>
            """

    return data


def get_chart(data):

    labels = []
    values = []

    for row in data:

        labels.append(row.expense_category)
        values.append(row.total_amount)

    chart = {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Expense Amount",
                    "values": values
                }
            ]
        },
        "type": "pie",
        "height": 300
    }

    return chart


def get_summary(data):

    total_expense = 0

    highest_category = ""

    highest_amount = 0

    for row in data:

        total_expense += row.total_amount or 0

        if row.total_amount > highest_amount:

            highest_amount = row.total_amount
            highest_category = row.expense_category

    summary = [

        {
            "label": "Total Expense",
            "value": total_expense,
            "datatype": "Currency"
        },

        {
            "label": "Highest Cost Category",
            "value": highest_category,
            "datatype": "Data"
        },

        {
            "label": "Highest Category Amount",
            "value": highest_amount,
            "datatype": "Currency"
        },

        {
            "label": "Categories Used",
            "value": len(data),
            "datatype": "Int"
        }

    ]

    return summary
