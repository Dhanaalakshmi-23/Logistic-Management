# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DriverExpenseDetail(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		expense_account: DF.Link | None
		expense_category: DF.Link
		expense_type: DF.Data | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		remarks: DF.SmallText | None
	# end: auto-generated types

	pass
