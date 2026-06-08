# Copyright (c) 2026, Dhanaa Lakshmi and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):

	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	summary = get_summary(data)

	return columns, data, None, chart, summary


def get_columns() -> list[dict]:

	return [
		{
			"label": _("Driver"),
			"fieldname": "driver",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 220
		},
		{
			"label": _("Total Trips"),
			"fieldname": "total_trips",
			"fieldtype": "Int",
			"width": 120
		},
		{
			"label": _("Total Expense"),
			"fieldname": "total_expense",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Total Payment"),
			"fieldname": "total_payment",
			"fieldtype": "Currency",
			"width": 150
		},
		{
			"label": _("Balance"),
			"fieldname": "balance",
			"fieldtype": "Currency",
			"width": 120
		},
		{
			"label": _("Risk Level"),
			"fieldname": "risk_level",
			"fieldtype": "Data",
			"width": 160
		}
	]


def get_data(filters=None):

	conditions = ""

	if filters:
		if filters.get("driver"):
			conditions += f" AND driver = '{filters.get('driver')}'"

		if filters.get("from_date") and filters.get("to_date"):
			conditions += f"""
				AND posting_date BETWEEN '{filters.get('from_date')}'
				AND '{filters.get('to_date')}'
			"""

	data = frappe.db.sql(f"""
		SELECT
			driver,
			COUNT(name) as total_trips,
			SUM(total_expense) as total_expense,
			SUM(total_advance) as total_advance
		FROM `tabTransport Trip`
		WHERE docstatus < 2
		{conditions}
		GROUP BY driver
	""", as_dict=1)

	result = []

	for d in data:

		expense = d.total_expense or 0
		advance = d.total_advance or 0
		balance = advance - expense

		if balance < -5000 or expense > 20000:
			risk = "High Risk"
		elif balance < 0:
			risk = "Medium Risk"
		else:
			risk = "Low Risk"

		result.append({
			"driver": d.driver,
			"total_trips": d.total_trips,
			"total_expense": expense,
			"total_payment": advance,
			"balance": balance,
			"risk_level": risk
		})

	return result


def get_chart(data):

	if not data:
		return None

	high = 0
	medium = 0
	low = 0

	total_loss = 0
	total_profit = 0

	for d in data:

		risk = d.get("risk_level")
		balance = d.get("balance") or 0

		if "High" in risk:
			high += 1
			total_loss += abs(balance)

		elif "Medium" in risk:
			medium += 1
			total_loss += abs(balance)

		elif "Low" in risk:
			low += 1
			total_profit += balance

	return {
		"data": {
			"labels": ["High Risk", "Medium Risk", "Low Risk"],
			"datasets": [
				{
					"name": "Drivers",
					"values": [high, medium, low]
				}
			]
		},
		"type": "donut"
	}


def get_summary(data):

	total_drivers = 0
	high_risk = 0
	medium_risk = 0

	for d in data:

		total_drivers += 1

		risk = d.get("risk_level")

		if "High" in risk:
			high_risk += 1

		elif "Medium" in risk:
			medium_risk += 1

	return [
		{
			"label": "Total Drivers",
			"value": total_drivers,
			"indicator": "blue"
		},
		{
			"label": "High Risk Drivers",
			"value": high_risk,
			"indicator": "red"
		},
		{
			"label": "Medium Risk Drivers",
			"value": medium_risk,
			"indicator": "orange"
		}
	]