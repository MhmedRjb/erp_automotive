// Copyright (c) 2024, highsoultion and contributors
// For license information, please see license.txt

frappe.ui.form.on("Delivery Note for Customs Card", {
    refresh(frm) {
        frm.set_query("part_type", () => {
            return {
                filters: {
                    name: ["in", ["Customer", "Supplier", "Employee", "Shareholder"]],
                },
            };
        });
    },
    customs_card: function(frm) {
        if (frm.doc.customs_card) {
            console.log('customs_card', frm.doc.customs_card);
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'customs card',
                    filters: { name: frm.doc.customs_card },
                    fieldname: 'current_holder'
                },
                callback: function(r) {
                    console.log("response from first call", r.message);
                    if (r.message && r.message.current_holder !== null) {
                        frm.set_value('holder_now', r.message.current_holder);
                    } else {
                        frm.set_value('holder_now', 'first-handq');
                    }
                }
            });
        }
    }
<<<<<<< HEAD
});
=======




});


 
>>>>>>> origin/before-merger
