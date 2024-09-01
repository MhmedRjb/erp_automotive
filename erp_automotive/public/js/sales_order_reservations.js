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


frappe.ui.form.on('Sales Order', {
    custom_item_group: async function(frm) {
        await fetchAndSetOptions(frm, 'custom_type', {
            item_group: frm.doc.custom_item_group
        });
    },
    custom_type: async function(frm) {
        await fetchAndSetOptions(frm, 'custom_category', {
            item_group: frm.doc.custom_item_group,
            templet: frm.doc.custom_type
        });
    },
    custom_category: async function(frm) {
        await fetchAndSetOptions(frm, 'custom_model', {
            item_group: frm.doc.custom_item_group,
            templet: frm.doc.custom_type,
            category: frm.doc.custom_category
        });
    },
    custom_model: async function(frm) {
        await fetchAndSetOptions(frm, 'custom_colour', {
            item_group: frm.doc.custom_item_group,
            templet: frm.doc.custom_type,
            category: frm.doc.custom_category,
            model: frm.doc.custom_model
        });
    },
    custom_colour: async function(frm) {
        try {
            let response = await frappe.call({
                method: 'erp_automotive.api.templet_list',
                args: {
                    item_group: frm.doc.custom_item_group,
                    templet: frm.doc.custom_type,
                    category: frm.doc.custom_category,
                    model: frm.doc.custom_model,
                    colour: frm.doc.custom_colour
                }
            });
            console.log('response:', response);
            let itemNames = response.message;
            console.log('itemNames:', itemNames);
            frm.set_value('custom_item_name', itemNames);
            frm.refresh_field('custom_item_name');
        } catch (error) {
            console.error('Error fetching item name:', error);
        }
    },
    custom_serial_no: async function(frm) {
        frm.set_query ("custom_serial_no",function(){
            return {
                filters: {
                    item_code: frm.doc.custom_item_name,
                }
            }
        })
            
    },
    custom_push: async function(frm, cdt, cdn) {
        let item = frm.add_child('items');
        item.item_code = frm.doc.custom_item_name;
        item.custom_serial_no_saver = frm.doc.custom_serial_no;
        frm.refresh_field('items');
    }


});



frappe.ui.form.on("Sales Order Item", {
    custom_add_serials: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        let existingSerials = [];
        if (row.custom_serial_no_saver && row.custom_serial_no_saver.length > 0) {
            existingSerials = row.custom_serial_no_saver.split('\n').filter(Boolean).map(serial => ({ serial_no: serial }));
        }
        
        openSerialNumberDialog(frm, row, existingSerials);
    },
    custom_serial_no_saver: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
    
        if (row.custom_serial_no_saver && row.custom_serial_no_saver.length > 0) {
            row.reserve_stock = 0; 
        } else {
            row.reserve_stock = 1; 
        }
        frm.refresh_field('items');

    },
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log('Item Code:', row.item_code);
        //remove the custom_serial_no_saver
        row.custom_serial_no_saver = '';
    },


});


function openSerialNumberDialog(frm, row, existingSerials) {

    let d = new frappe.ui.Dialog({
        title: 'Reserved Serials',
        size: 'extra-large',
        fields: [
            {
                label: 'Item Code',
                fieldname: 'item_code',
                fieldtype: 'Data',
                read_only: 1,
                default: row.item_code
            },
            {
                label: 'Warehouse',
                fieldname: 'warehouse',
                fieldtype: 'Data',
                read_only: 1,
                default: row.warehouse
            },
            {
                label: 'Quantity',
                fieldname: 'qty',
                fieldtype: 'Data',
                read_only: 1,
                default: row.qty
            },
            {
                fieldname: "items",
                fieldtype: "Table",
                label: __("Items to Reserve"),
                size: "extra-large",
                data: existingSerials,
                fields: [
                    {
                        fieldname: "serial_no",
                        fieldtype: "Link",
                        label: __("serial no"),
                        options: "Serial No",
                        in_list_view: 1,
                        get_query: () => {
                            return {
                                filters: {
                                    item_code: row.item_code,
                                    status: "Active",
                                    custom_reservation_status:"un Reserved"
                                }
                            };
                        }
                    },
                ],
            },
        ],
        primary_action_label: 'Submit',
        primary_action(values) {
        let items = d.get_values().items;
        let serials = items.map(item => item.serial_no).join('\n'); 
            row.custom_serial_no_saver = serials;
            row.reserve_stock = serials.length > 0 ? 0 : 1; 

        

        let uniqueSerials = new Set(serials.split('\n'));
        if (uniqueSerials.size !== serials.split('\n').length) {
            
            var uniqueSerialsArray = Array.from(uniqueSerials);
            console.log('uniqueSerialsArray:', uniqueSerialsArray);
            frappe.msgprint(__('Duplicate serial numbers are not allowed.'));
            serials=d.get_values().items;
            d.set_value('items', uniqueSerialsArray);
            console.log('uniquessssSerials:', uniqueSerials);
            console.log('doc.get_values().items:', serials);
            return;
        }



            frm.refresh_field('items');

            d.hide();  
        }
    });

    d.show();
}

function checkAndSetReserveStock(row) {
    if (row.custom_serial_no_saver && row.custom_serial_no_saver.length > 0) {
        row.reserve_stock = 1;
    } else {
        row.reserve_stock = 0;
    }
    cur_frm.refresh_field('items');
}


