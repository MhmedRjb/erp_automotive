// Copyright (c) 2024, highsoultion and contributors
// For license information, please see license.txt
async function fetchAndSetOptions(frm, field, args) {
    try {
        let response = await frappe.call({
            method: 'erp_automotive.api.templet_list',
            args: args
        });
        let itemNames = response.message;
        frm.set_df_property(field, 'options', itemNames);
        frm.refresh_field(field);
    } catch (error) {
        console.error('Error fetching options:', error);
    }
}

frappe.ui.form.on("Car Chooser", {
    item_group: async function(frm) {
        await fetchAndSetOptions(frm, 'type', {
            item_group: frm.doc.item_group
        });
    },
    type: async function(frm) {
        await fetchAndSetOptions(frm, 'category', {
            item_group: frm.doc.item_group,
            templet: frm.doc.type
        });
    },
    category: async function(frm) {
        await fetchAndSetOptions(frm, 'model', {
            item_group: frm.doc.item_group,
            templet: frm.doc.type,
            category: frm.doc.category
        });
    },
    model: async function(frm) {
        await fetchAndSetOptions(frm, 'colour', {
            item_group: frm.doc.item_group,
            templet: frm.doc.type,
            category: frm.doc.category,
            model: frm.doc.model
        });
    },
    colour: async function(frm) {
        try {
            let response = await frappe.call({
                method: 'erp_automotive.api.templet_list',
                args: {
                    item_group: frm.doc.item_group,
                    templet: frm.doc.type,
                    category: frm.doc.category,
                    model: frm.doc.model,
                    colour: frm.doc.colour
                }
            });
            console.log('response:', response);
            let itemNames = response.message;
            console.log('itemNames:', itemNames);
            frm.set_value('item_name', itemNames);
            frm.refresh_field('item_name');
        } catch (error) {
            console.error('Error fetching item name:', error);
        }
    },
    serial_no: async function(frm) {
        frm.set_query ("serial_no",function(){
            return {
                filters: {
                    item_code: frm.doc.item_name,
                }
            }
        })
            
    },
    push: async function(frm, cdt, cdn) {
        //make a dict to test push seril and item to the child table in  table
        let response = await frappe.call({
            method: 'erp_automotive.api.templet_list',
            args: {
                item_group: frm.doc.item_group,
                templet: frm.doc.type,
                category: frm.doc.category,
                model: frm.doc.model,
                colour: frm.doc.colour,
                sn:1
            }
        });
        
        let itemwiththeSerial = response.message;
        console.log('itemwiththeSerial:', itemwiththeSerial);
        for (let product in itemwiththeSerial) {
            if (itemwiththeSerial.hasOwnProperty(product)) {
                let serialNumbers = itemwiththeSerial[product];
                for (let serial of serialNumbers) {
                    let item = frm.add_child('items');
                    item.item_code = product; // Assuming product name should be used as item_code
                    item.custom_serial_no_saver = serial;
                    item.custom_serial_no = serial;
                }
            }
        }
        frm.refresh_field('items');
        },

	refresh(frm) {
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




