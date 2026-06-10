# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data)

	return columns, data, None, chart


def get_columns():

	return [

		{
			"label": "Current Default Advance",
			"fieldname": "current_advance",
			"fieldtype": "Currency",
			"width": 180
		},

		{
			"label": "Trips Analysed",
			"fieldname": "trip_count",
			"fieldtype": "Int",
			"width": 140
		},

		{
			"label": "Total Expense",
			"fieldname": "total_expense",
			"fieldtype": "Currency",
			"width": 150
		},

		{
			"label": "Average Expense",
			"fieldname": "average_expense",
			"fieldtype": "Currency",
			"width": 150
		},

		{
			"label": "Highest Expense",
			"fieldname": "highest_expense",
			"fieldtype": "Currency",
			"width": 150
		},

		{
			"label": "Lowest Expense",
			"fieldname": "lowest_expense",
			"fieldtype": "Currency",
			"width": 150
		},

		{
			"label": "Recommended Advance",
			"fieldname": "recommended_advance",
			"fieldtype": "Currency",
			"width": 180
		},

		{
			"label": "Difference",
			"fieldname": "difference",
			"fieldtype": "Currency",
			"width": 130
		},

		{
			"label": "Action Required",
			"fieldname": "recommendation",
			"fieldtype": "Data",
			"width": 220
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

	trips = frappe.db.sql(
		f"""
		SELECT
			total_expense
		FROM `tabTransport Trip`
		WHERE
			docstatus = 1
			AND total_expense > 0
			{conditions}
		""",
		filters,
		as_dict=True
	)

	if not trips:
		return []

	settings = frappe.get_single("Default Trip Settings")

	current_advance = settings.default_advance_amount or 0

	total_expense = 0
	highest_expense = 0
	lowest_expense = trips[0].total_expense

	for row in trips:
		expense = row.total_expense or 0
		total_expense += expense
		if expense > highest_expense:
			highest_expense = expense
		if expense < lowest_expense:
			lowest_expense = expense

	average_expense = total_expense / len(trips)
	recommended_advance = round(average_expense + 200)
	difference = recommended_advance - current_advance

	if difference > 0:

		recommendation = f"""
		<span style="color:red;font-weight:bold;">
			Increase Advance by ₹{difference}
		</span>
		"""

	elif difference < 0:

		recommendation = f"""
		<span style="color:green;font-weight:bold;">
			Reduce Advance by ₹{abs(difference)}
		</span>
		"""

	else:

		recommendation = """
		<span style="color:blue;font-weight:bold;">
			Current Advance is Optimal
		</span>
		"""

	data = [{
		"current_advance": current_advance,
		"trip_count": len(trips),
		"total_expense": total_expense,
		"average_expense": average_expense,
		"highest_expense": highest_expense,
		"lowest_expense": lowest_expense,
		"recommended_advance": recommended_advance,
		"difference": difference,
		"recommendation": recommendation
	}]

	return data


def get_chart_data(data):

	if not data:
		return None

	row = data[0]

	return {
		"data": {
			"labels": [
				"Current Advance",
				"Recommended Advance"
			],
			"datasets": [
				{
					"values": [
						row["current_advance"],
						row["recommended_advance"]
					]
				}
			]
		},
		"type": "bar",
		"height": 300
	}