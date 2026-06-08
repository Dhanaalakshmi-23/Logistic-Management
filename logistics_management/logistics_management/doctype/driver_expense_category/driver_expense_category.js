// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Driver Expense Category", {
	setup(frm) {
        frm.set_query("expense_account", function() {
            return {
                filters: {
                    is_group: 0,
                    root_type: "Expense",
                    company:frm.doc.company
                }
            };
        });
	},
});
