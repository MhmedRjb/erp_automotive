frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        console.log(frm);
        // Existing button
        frm.add_custom_button(__('Create Customs Card Receipt'), function(){
            frappe.new_doc('customs card receipt', {}, inv => {
                inv.supplier = frm.doc.supplier;
                inv.purchase_receipt_no= frm.doc.name;
                inv.supplier_delivery_note = frm.doc.supplier_delivery_note;
                frm.doc.items.forEach(item => {
                    // Check if the item has serial numbers
                    if (item.serial_no) {
                        // Split the serial numbers based on the quantity
                        let serial_numbers = item.serial_no.split('\n');
                        for (let i = 0; i < item.qty; i++) {
                            let inv_item = frappe.model.add_child(inv, 'items');
                            inv_item.item_code = item.item_code;
                            inv_item.serial_no = serial_numbers[i] || ''; // Assign serial number or empty string if not available
                            inv_item.customs_card = item.customs_card;
                        }
                    } else {
                        // If no serial numbers, add the item only once
                        let inv_item = frappe.model.add_child(inv, 'items');
                        inv_item.item_code = item.item_code;
                        inv_item.serial_no = '555555555'; // No serial number
                        inv_item.customs_card = item.customs_card;
                    }
                });
            });
            // frappe.msgprint("Customs Card Receipt created!");
        }, __("Create"));

        // New button
        frm.add_custom_button(__('Popup'), function(){
            // Create a new dialog
            let d = new frappe.ui.Dialog({
                title: __('New Customs Card Receipt'),
                fields: [
                    {
                        fieldtype: 'Link',
                        fieldname: 'supplier',
                        label: __('Supplier'),
                        options: 'Supplier',
                        reqd: 1
                    },
                    {
                        fieldtype: 'Data',
                        fieldname: 'purchase_receipt_no',
                        label: __('Purchase Receipt No'),
                        reqd: 1
                    },
                    {
                        fieldtype: 'Data',
                        fieldname: 'supplier_delivery_note',
                        label: __('Supplier Delivery Note')
                    },
                    {
                        fieldtype: 'Table',
                        fieldname: 'items',
                        label: __('Items'),
                        fields: [
                            {
                                fieldtype: 'Link',
                                fieldname: 'item_code',
                                label: __('Item Code'),
                                options: 'Item',
                                reqd: 1
                            },
                            {
                                fieldtype: 'Data',
                                fieldname: 'serial_no',
                                label: __('Serial No')
                            },
                            {
                                fieldtype: 'Data',
                                fieldname: 'customs_card',
                                label: __('Customs Card')
                            }
                        ]
                    }
                ],
                primary_action_label: __('Create'),
                primary_action(values) {
                    frappe.call({
                        method: 'frappe.client.insert',
                        args: {
                            doc: {
                                doctype: 'Customs Card Receipt',
                                supplier: values.supplier,
                                purchase_receipt_no: values.purchase_receipt_no,
                                supplier_delivery_note: values.supplier_delivery_note,
                                items: values.items
                            }
                        },
                        callback: function(r) {
                            if (!r.exc) {
                                frappe.msgprint(__('Customs Card Receipt created successfully'));
                                d.hide();
                            }
                        }
                    });
                }
            });

            // Show the dialog
            d.show();
        }, __("Create"));
    }
});