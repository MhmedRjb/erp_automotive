frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        console.log(frm);
        
        frm.add_custom_button(__('Create Customs Card Receipt'), function() {
            // Create new Customs Card Receipt
            frappe.new_doc('customs card receipt', {}, doc => {
                doc.supplier = frm.doc.supplier;
                doc.purchase_receipt_no = frm.doc.name;
                doc.supplier_delivery_note = frm.doc.supplier_delivery_note;
                frm.doc.items.forEach(item => {
                    let serial_numbers = item.serial_no.split('\n');
                    serial_numbers.forEach((serial_no, index) => {
                        if (index < item.qty) {
                            frappe.call({
                                method: 'frappe.client.get_value',
                                args: {
                                    doctype: 'Serial No',
                                    filters: { name: serial_no },
                                    fieldname: 'customs_card'
                                },
                                async: false,
                                callback: function(response) {
                                    let customs_card = response.message ? response.message.customs_card : '';
                                    if  (!customs_card) {
                                        let inv_item = frappe.model.add_child(doc, 'items');
                                        inv_item.item_code = item.item_code;
                                        inv_item.serial_no = serial_no || ''; 
                                        inv_item.customs_card = customs_card;
    
                                    }
                                }
                            });
                        }
                    });
                });
            });
        }, __("Create"));
    }
});
