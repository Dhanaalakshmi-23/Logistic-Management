// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Transport Trip", {
    refresh(frm) {

        if (frm.doc.docstatus === 1 && frm.doc.advance_jv) {

            frm.add_custom_button(
                "View Advance JE",
                function () {

                    frappe.set_route(
                        "Form",
                        "Journal Entry",
                        frm.doc.advance_jv
                    );

                }
            );
        }

            if (frm.doc.docstatus === 1 && frm.doc.bus_ownership === "Rental Bus" && !frm.doc.rental_expense) {

            frm.add_custom_button(
                "Create Rental Expense",
                function () {

                    frappe.new_doc("Driver Expense Entry", {
                        transport_trip: frm.doc.name,
                        supplier: frm.doc.supplier,
                        posting_date: frappe.datetime.get_today(),
                        expense_type: "Rental Bus Expense",
                        amount: frm.doc.rental_amount
                    });

                }
            );
        }
        if(frm.doc.doctstatus===1 && frm.doc.rental_expense_jv){
            frm.add_custom_button("View Rental Expense JE", 
                function(){
                    frappe.set_route(
                        "Form",
                        "Journal Entry",
                        frm.doc.rental_expense_jv
                    );
                }
            );
        }
    },


    setup(frm) {

        frm.set_query("driver", function() {

            return {
                filters: {
                    status: "Active",
                    designation: "Driver"
                }
            };

        });


        frm.set_query("bus_assest", function () {

            return {
                filters: {
                    asset_category: "Vehicles"
                }
            };
        });

        frm.set_query("supplier", function () {

            return {
                filters: {
                    disabled: 0
                }
            };

        });
    }
});
