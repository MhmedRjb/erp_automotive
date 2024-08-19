frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        console.log(frm);
        // if (frm.doc.status === "Draft") { }
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
    }
});