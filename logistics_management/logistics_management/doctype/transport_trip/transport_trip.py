# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TransportTrip(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		advance_given_to_driver: DF.Currency
		advance_jv: DF.Link | None
		amended_from: DF.Link | None
		balance_amount: DF.Currency
		bus_assest: DF.Link | None
		bus_ownership: DF.Literal["Owned Bus", "Rental Bus"]
		company: DF.Link
		destination: DF.Data | None
		driver: DF.Link
		driver_name: DF.Data | None
		end_date_time: DF.Datetime | None
		rental_amount: DF.Currency
		rental_expense_jv: DF.Link | None
		rental_vehicle_number: DF.Data | None
		source: DF.Data | None
		start_date_time: DF.Datetime | None
		status: DF.Literal["Draft", "Scheduled", "In Progress", "Completed", "Cancelled", "Settled"]
		supplier: DF.Link | None
		total_advance: DF.Currency
		total_expense: DF.Currency
		trip_date: DF.Date
	# end: auto-generated types

	def on_submit(self):
		jv = self.create_advance_jv()
		self.db_set("advance_jv",jv.name)
		
		existing = frappe.db.exists("Driver Advance Audit",{
			"transport_trip":self.name
		})
		if not existing:
			self.create_driver_advance(jv.name)
		self.db_set("total_advance", self.advance_given_to_driver)
		self.db_set("status", "In Progress")


	def validate(self):
		self.validate_vehicle()
		self.validate_dates()
		self.validate_advance()

	def on_cancel(self):

		if self.advance_jv:
			jv = frappe.get_doc("Journal Entry",self.advance_jv)
			if jv.docstatus == 1:
				jv.cancel()

		if self.rental_expense_jv:
			jv = frappe.get_doc("Journal Entry",self.rental_expense_jv)
			if jv.docstatus == 1:
				jv.cancel()

	def create_advance_jv(self):
		cash_acc = self.get_cash_account()
		advance_acc = self.get_driver_advance_account()
		jv = frappe.new_doc("Journal Entry")
		jv.voucher_type = "Cash Entry"
		jv.posting_date = self.trip_date
		jv.company = self.company
		jv.append("accounts",
			{
				"account":advance_acc,
				"debit_in_account_currency":self.advance_given_to_driver,
			})
		jv.append("accounts",
			{
				"account":cash_acc,
				"credit_in_account_currency":self.advance_given_to_driver
			})
		jv.insert(ignore_permissions=True)
		jv.submit()
		return jv
	
	def create_driver_advance(self,jv_name):
		doc = frappe.new_doc("Driver Advance Audit")
		doc.transport_trip = self.name
		doc.driver = self.driver
		doc.advance_amount = self.advance_given_to_driver
		doc.posting_date = self.trip_date
		doc.advance_journal_entry = jv_name
		doc.insert(ignore_permissions=True)
		doc.submit()
	
	def get_cash_account(self):
		acc = frappe.db.get_value("Account", {
			"account_name":"Cash",
			"company":self.company,
			"is_group":0
		},"name")
		if not acc:
			frappe.throw("Cash Account Not Found")
		return acc
	
	def get_driver_advance_account(self):
		acc = frappe.db.get_value("Account", {
            "account_name": "Driver Advance",
            "company": self.company,
            "is_group": 0
        },"name")
		if not acc:
			frappe.throw("Driver Advance Account not found")
		return acc

	
	def validate_vehicle(self):
		if self.bus_ownership=="Owned Bus":
			if not self.bus_assest:
				frappe.throw("Please Select Bus Assest")

		elif self.bus_ownership == "Rental Bus":
			if not self.supplier:
				frappe.throw("Please Select Supplier")
			if not self.rental_vehicle_number:
				frappe.throw("Please enter Rental Vehicle Number")
			if not self.rental_amount:
				frappe.throw("Rental Amount is Mandatory")
			if self.rental_amount <= 0:
				frappe.throw("Rental Amount should be Greater than Zero")

	def validate_dates(self):
		if (self.start_date_time and self.end_date_time and self.end_date_time < self.start_date_time):
			frappe.throw("End Date Time cannot be before Start Date Time")

	def validate_advance(self):
		if self.advance_given_to_driver == 0:
			frappe.throw("Advance Amount should be greater than zero")

@frappe.whitelist()
def create_rental_expense_je(trip):
	trip_doc = frappe.get_doc("Transport Trip", trip)
	if trip_doc.rental_expense_jv:
		frappe.throw("Rental Expense JE already created")
	if trip_doc.bus_ownership != "Rental Bus":
		frappe.throw("This trip is not a Rental Bus Trip")
	jv = frappe.new_doc("Journal Entry")
	jv.voucher_type = "Journal Entry"
	jv.company = trip_doc.company
	jv.posting_date = frappe.utils.today()
	jv.append("accounts",{
        "account":"Vehicle Rental Expense - DLPL",
        "debit_in_account_currency":trip_doc.rental_amount
    })
	jv.append("accounts",{
		"account": "Creditors - DLPL",
		"credit_in_account_currency": trip_doc.rental_amount,
		"party_type": "Supplier",
		"party": trip_doc.supplier
	})
	jv.insert(ignore_permissions=True)
	jv.submit()
	trip_doc.db_set("rental_expense_jv",jv.name)
	return jv.name

