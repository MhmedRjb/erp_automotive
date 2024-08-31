// Copyright (c) 2024, highsoultion and contributors
// For license information, please see license.txt

frappe.ui.form.on("Car Chooser", {
	refresh(frm) {
        //fetch all item to items child table based on the item_group
        frm.add_custom_button(__('Fetch Items'), function() {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Item",
                    item_group: frm.doc.item_group
                },
                callback: function(r) {
                    if(r.message) {
                        frm.clear_table("items");
                        console.log(r.message);

                        r.message.forEach(function(item) {
                            frm.add_child("items", {
                                item_code: item.name,
                            });
                        });
                        frm.refresh_field("items");
                    }
                }
            });
        });

	},
});
