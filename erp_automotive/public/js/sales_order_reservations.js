frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        console.log("tesst");
        frm.set_query("custom_serial_no", "items", function (doc, cdt, cdn) {
          return {
            "filters": {
              "item_name": "item_code"
            },
          };
        });
    }
});

frappe.ui.form.on("Sales Order Item", {
    custom_add_serials: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log('Row:', row);

        // Check if custom_serial_no_saver is empty
        let existingSerials = [];
        if (row.custom_serial_no_saver && row.custom_serial_no_saver.length > 0) {
            existingSerials = row.custom_serial_no_saver.split('\n').filter(Boolean).map(serial => ({ serial_no: serial }));
        }
        
        openSerialNumberDialog(frm, row, existingSerials);
    },
    custom_serial_no_saver: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log('Serials changed:', row.custom_serial_no_saver);
    
        // Check and set reserve_stock based on custom_serial_no_saver
        if (row.custom_serial_no_saver && row.custom_serial_no_saver.length > 0) {
            row.reserve_stock = 0; // Unchecked
        } else {
            row.reserve_stock = 1; // Checked
        }
        // Refresh the field to reflect the change
        frm.refresh_field('items');

    },
    item_code: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        console.log('Item Code:', row.item_code);
        //remove the custom_serial_no_saver
        row.custom_serial_no_saver = '';
    },


});


// Function to open the dialog and add serial numbers
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
                                    item_code: row.item_code
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

