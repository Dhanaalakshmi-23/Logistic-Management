# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DriverExpenseCategory(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		category_name: DF.Data
		company: DF.Link
		expense_account: DF.Link
		expense_type: DF.Literal["Company Expense", "Driver Expense", "Trip Expense"]
	# end: auto-generated types

	pass