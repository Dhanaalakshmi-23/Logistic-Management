# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DriverExpenseEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.logistics_management.doctype.driver_expense_detail.driver_expense_detail import DriverExpenseDetail
		from frappe.types import DF

		advance_amount: DF.Currency
		amended_from: DF.Link | None
		balance_amount: DF.Currency
		driver: DF.Link
		driver_name: DF.Data | None
		expense_detail: DF.Table[DriverExpenseDetail]
		expense_je: DF.Link | None
		posting_date: DF.Date
		settlement_journal_entry: DF.Link | None
		total_expense: DF.Currency
		trip: DF.Link
	# end: auto-generated types

	pass

	def validate(self):
		self.validate_duplicate_trip()
		self.validate_expense_rows()
		self.fetch_advance_amount()
		self.calculate_totals()
		self.calculate_balance()
		#self.validate_fuel_expenses()

	def on_submit(self):
		self.update_trip_summary()

	def on_cancel(self):
		self.cancel_expense_je()
		self.cancel_settlement_je()
		self.reset_trip_summary()

	def cancel_expense_je(self):
		if not self.expense_je:
			return

		try:
			je = frappe.get_doc("Journal Entry", self.expense_je)

			if je.docstatus == 1:
				je.cancel()

		except Exception as e:
			frappe.throw(f"Error cancelling Expense JE: {e}")
		self.db_set("expense_je", None)
	def cancel_settlement_je(self):
		if not self.settlement_journal_entry:
			return

		try:
			je = frappe.get_doc("Journal Entry", self.settlement_journal_entry)

			if je.docstatus == 1:
				je.cancel()

		except Exception as e:
			frappe.throw(f"Error cancelling Settlement JE: {e}")

		# unlink
		self.db_set("settlement_journal_entry", None)

	def reset_trip_summary(self):
		trip = frappe.get_doc("Transport Trip", self.trip)
		trip.db_set("total_expense", 0)
		trip.db_set("balance_amount", 0)
		trip.db_set("status", "Open")

	def validate_duplicate_trip(self):
		existing = frappe.db.exists(
			"Driver Expense Entry",
			{
				"trip": self.trip,
				"docstatus": 1,
				"name": ["!=", self.name]
			}
		)

		if existing:
			frappe.throw("Expense Entry already exists for this Trip")

	def validate_expense_rows(self):
		if not self.expense_detail:
			frappe.throw("At least one Expense Detail is required")

		for row in self.expense_detail:
			if row.amount <= 0:
				frappe.throw(f"Amount must be greater than 0 (Row {row.idx})")


	def fetch_advance_amount(self):
		self.advance_amount = frappe.db.get_value(
			"Transport Trip",
			self.trip,
			"advance_given_to_driver"
		) or 0

	def calculate_totals(self):
		total = 0
		for row in self.expense_detail:
			total = total + row.amount
		self.total_expense = total

	def calculate_balance(self):
		self.balance_amount = self.advance_amount - self.total_expense

	# def validate_fuel_expenses(self):
	# 	settings = frappe.get_single("Default Trip Settings")
	# 	petrol_rate = settings.default_petrol_rate or 0
	# 	total_fuel_quantity = 0

	# 	for row in self.expense_detail:
	# 		if row.expense_category == "Fuel":
	# 			if row.fuel_quantity == 0:
	# 				frappe.throw(f"Fuel Quantity must be greater than zero (Row {row.idx})")
	# 			row.expected_amount = row.fuel_quantity * petrol_rate
	# 			total_fuel_quantity += row.fuel_quantity

	# 	trip = frappe.get_doc("Transport Trip",self.trip)

	# 	if (trip.distance_travelled and trip.vehicle_mileage):

	# 		expected_fuel = trip.distance_travelled / trip.vehicle_mileage

	# 		allowed_fuel = expected_fuel * 1.20

	# 		if total_fuel_quantity > allowed_fuel:
	# 			frappe.throw(
	# 				f"""
	# 				Possible Fuel Fraud Detected.<br><br>
	# 				Expected Fuel Consumption : {expected_fuel:.2f} L<br>
	# 				Allowed Fuel Consumption : {allowed_fuel:.2f} L<br>
	# 				Claimed Fuel Quantity : {total_fuel_quantity:.2f} L
	# 				"""
	# 			)
	def update_trip_summary(self):
		trip = frappe.get_doc("Transport Trip", self.trip)
		trip.db_set("total_expense", self.total_expense)
		trip.db_set("balance_amount", self.balance_amount)
		if self.balance_amount > 0:
			trip.db_set("settlement_status", "Payable by Driver")

		elif self.balance_amount < 0:
			trip.db_set("settlement_status", "Payable by Company")

		else:
			trip.db_set("settlement_status", "Cleared")
		trip.db_set("status", "Completed")


@frappe.whitelist()
def create_expense_je(expense_entry):

	doc = frappe.get_doc("Driver Expense Entry", expense_entry)

	if doc.expense_je:
		frappe.throw("Expense JE already exists")

	trip = frappe.get_doc("Transport Trip", doc.trip)

	jv = frappe.new_doc("Journal Entry")
	jv.voucher_type = "Journal Entry"
	jv.company = trip.company
	jv.posting_date = doc.posting_date
	jv.remark = f"Driver Expense - {doc.name}"

	total = 0

	for row in doc.expense_detail:
		jv.append("accounts", {
			"account": row.expense_account,
			"debit_in_account_currency": row.amount
		})
		total += row.amount

	jv.append("accounts", {
		"account": "Driver Advance - DLPL",
		"credit_in_account_currency": total
	})

	jv.insert(ignore_permissions=True)
	jv.submit()

	doc.db_set("expense_je", jv.name)

	return jv.name



@frappe.whitelist()
def create_settlement_je(expense_entry):

	doc = frappe.get_doc("Driver Expense Entry", expense_entry)

	if doc.settlement_journal_entry:
		frappe.throw("Settlement JE already exists")

	if not doc.expense_je:
		frappe.throw("Create Expense JE first")

	balance = doc.balance_amount

	if balance == 0:
		frappe.throw("No balance to settle")

	trip = frappe.get_doc("Transport Trip", doc.trip)

	jv = frappe.new_doc("Journal Entry")
	jv.voucher_type = "Journal Entry"
	jv.company = trip.company
	jv.posting_date = doc.posting_date
	jv.remark = f"Driver Settlement - {doc.name}"

	if balance > 0:
		jv.append("accounts", {
			"account": "Cash",
			"company": trip.company,
			"debit_in_account_currency": balance
		})
		jv.append("accounts", {
			"account": "Driver Advance",
			"company" :trip.company,
			"credit_in_account_currency": balance
		})

	else:
		amount = abs(balance)

		jv.append("accounts", {
			"account": "Driver Advance",
			"company" :trip.company,
			"debit_in_account_currency": amount
		})
		jv.append("accounts", {
			"account": "Cash",
			"company" :trip.company,
			"credit_in_account_currency": amount
		})

	jv.insert(ignore_permissions=True)
	jv.submit()

	frappe.db.set_value("Driver Expense Entry", doc.name, {
		"settlement_journal_entry": jv.name,
		"balance_amount": 0
	})

	frappe.db.set_value("Transport Trip", doc.trip, {
		"balance_amount": 0,
		"settlement_status": "Cleared",
		"settlement_journal_entry": jv.name,
		"status": "Settled"
	})
	return jv.name
