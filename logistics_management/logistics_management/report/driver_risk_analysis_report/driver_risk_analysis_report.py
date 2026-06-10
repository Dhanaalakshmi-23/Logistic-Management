# Copyright (c) 2026, Frappe Technologies and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    filters = filters or {}

    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)

    return columns, data, None, chart


def get_columns():
    return [
        {
            "label": "Driver",
            "fieldname": "driver",
            "fieldtype": "Link",
            "options": "Employee",
            "width": 140
        },
        {
            "label": "Driver Name",
            "fieldname": "driver_name",
            "fieldtype": "Data",
            "width": 180
        },
        {
            "label": "Trips",
            "fieldname": "trip_count",
            "fieldtype": "Int",
            "width": 90
        },
        {
            "label": "Total Advance",
            "fieldname": "total_advance",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": "Total Expense",
            "fieldname": "total_expense",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": "Fuel",
            "fieldname": "fuel",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "label": "Toll",
            "fieldname": "toll",
            "fieldtype": "Currency",
            "width": 110
        },
        {
            "label": "Food + Tea",
            "fieldname": "food_tea",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Variance",
            "fieldname": "variance",
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "label": "Suspicious Area",
            "fieldname": "suspicious_area",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": "Risk Level",
            "fieldname": "risk_level",
            "fieldtype": "Data",
            "width": 120
        }
    ]


def get_data(filters):
    conditions = ""

    if filters.get("driver"):
        conditions += " and dee.driver = %(driver)s"

    data = frappe.db.sql(
        f"""
			select
				dee.driver,
				dee.driver_name,
				count(distinct dee.name) as trip_count,
				sum(dee.advance_amount) as total_advance,
				sum(dee.total_expense) as total_expense,

				sum(case when ded.expense_category = 'Fuel' then ded.amount else 0 end) as fuel,
				sum(case when ded.expense_category = 'Toll' then ded.amount else 0 end) as toll,
				sum(case when ded.expense_category in ('Food', 'Tea') then ded.amount else 0 end) as food_tea

			from `tabDriver Expense Entry` dee
			left join `tabDriver Expense Detail` ded
				on dee.name = ded.parent

			where dee.docstatus = 1
			{conditions}

			group by dee.driver, dee.driver_name
			order by total_expense desc
		""",
        filters,
        as_dict=True,
    )

    for row in data:

        fuel = row.fuel or 0
        toll = row.toll or 0
        food_tea = row.food_tea or 0
        total_expense = row.total_expense or 0
        total_advance = row.total_advance or 0

        row.variance = total_advance - total_expense

        highest = max(fuel, toll, food_tea)

        if highest == fuel:
            row.suspicious_area = "Fuel"
        elif highest == toll:
            row.suspicious_area = "Toll"
        else:
            row.suspicious_area = "Food/Tea"

        risk_score = 0

        if total_expense > total_advance:
            risk_score += 50

        if total_expense and fuel > (total_expense * 0.60):
            risk_score += 20
        if total_expense and toll > (total_expense * 0.30):
            risk_score += 15
        if total_expense and food_tea > (total_expense * 0.20):
            risk_score += 15

        if risk_score >= 50:
            row.risk_level = "High"
        elif risk_score >= 20:
            row.risk_level = "Medium"
        else:
            row.risk_level = "Low"

    return data


def get_chart(data):

    if not data:
        return None

    fuel = 0
    toll = 0
    food_tea = 0

    for row in data:
        fuel += row.fuel or 0
        toll += row.toll or 0
        food_tea += row.food_tea or 0

    return {
        "data": {
            "labels": ["Fuel", "Toll", "Food + Tea"],
            "datasets": [
                {
                    "values": [fuel, toll, food_tea]
                }
            ]
        },
        "type": "pie",
        "title": "Expense Category Distribution"
    }