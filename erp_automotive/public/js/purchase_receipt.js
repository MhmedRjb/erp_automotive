frappe.ui.form.on('Purchase Receipt', {
    refresh: function(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Customs Card Receipt'), function(){
                frappe.new_doc('customs card receipt', {}, inv => {
                    inv.supplier = frm.doc.supplier;
                    frm.doc.items.forEach(items => {
                        let inv_item = frappe.model.add_child(inv, 'items');
                        inv_item.item_code = items.item_code;
                        inv_item.serial_no = items.serial_no;
                        inv_item.customs_card = items.customs_card;
                    });
                });
                // frappe.msgprint("Customs Card Receipt created!");
            }, __("Create"));
        }
    }
});