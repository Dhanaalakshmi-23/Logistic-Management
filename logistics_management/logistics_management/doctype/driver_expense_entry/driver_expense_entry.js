// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt


frappe.ui.form.on("Driver Expense Entry", {

	setup(frm) {
		frm.set_query("trip", function () {
			return {
				filters: {
					docstatus: 1
				}
			};
		});
	},

	trip(frm) {
		if (!frm.doc.trip) return;

		frappe.db.get_doc("Transport Trip", frm.doc.trip).then(doc => {
			frm.set_value("driver", doc.driver);
			frm.set_value("driver_name", doc.driver_name);
		});
	},

	refresh(frm) {

        if (frm.doc.docstatus === 1 && !frm.doc.expense_je) {
			frm.add_custom_button("Create Expense JE", () => {
				frappe.call({
					method: "erpnext.logistics_management.doctype.driver_expense_entry.driver_expense_entry.create_expense_je",
					args: { expense_entry: frm.doc.name },
					callback: function (r) {
						if (r.message) {
							frappe.msgprint("Expense JE Created Successfully");
							frm.reload_doc();
						}
					}
				});
			});
		}

		if (frm.doc.expense_je) {
			frm.add_custom_button("View Expense JE", () => {
				frappe.set_route("Form", "Journal Entry", frm.doc.expense_je);
			});
		}

		if (frm.doc.docstatus === 1 && frm.doc.expense_je && !frm.doc.settlement_journal_entry) {
			frm.add_custom_button("Create Settlement JE", () => {
				frappe.call({
					method: "erpnext.logistics_management.doctype.driver_expense_entry.driver_expense_entry.create_settlement_je",
					args: { expense_entry: frm.doc.name },
					callback: function (r) {
						if (r.message) {
							frappe.msgprint("Settlement JE Created Successfully");
							frm.reload_doc();
						}
					}
				});
			});
		}

		if (frm.doc.settlement_journal_entry) {
			frm.add_custom_button("View Settlement JE", () => {
				frappe.set_route("Form", "Journal Entry", frm.doc.settlement_journal_entry);
			});
		}
	}
});
