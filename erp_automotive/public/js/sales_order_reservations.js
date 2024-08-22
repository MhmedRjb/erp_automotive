frappe.ui.form.on('Sales Order', {
    refresh: function(frm) {
        console.log("tesst"),
        frm.set_query("custom_serial_no", "items", function (doc, cdt, cdn) {
          return {
            "filters": {
              "item_name": "item_code"
            },
          };
        });
    }
});

frappe.ui.form.on('Sales Order Item', {
    custom_add_serials: async function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];        
        let d = new frappe.ui.Dialog({
            title: 'Reserved Serials',
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
                    label: 'Serial Numbers',
                    fieldname: 'serial_numbers',
                    fieldtype: 'Table',
                    fields: [
                        {
                            fieldtype: 'Link',
                            fieldname: 'serial_no',
                            label: 'Serial No',
                            options: 'Serial No',
                            in_list_view: 1,
                        }
                    ]
                }
            ],
            primary_action_label: 'Save',
            primary_action(values) {
                let serial_numbers = values.serial_numbers.map(row => row.serial_no);
                console.log(serial_numbers);
                d.hide();
            }
        });

        // Show the dialog
        d.show();
    }
});