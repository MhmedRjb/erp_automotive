// Copyright (c) 2024, highsoultion and contributors
// For license information, please see license.txt

frappe.ui.form.on("customs card", {
    refresh(frm) {
        frm.add_custom_button(__('Create Delivery Note'), function() {
            frappe.new_doc('Delivery Note for Customs Card', {
                customs_card: frm.doc.name
            });
        }, __('Actions'));
    },
});