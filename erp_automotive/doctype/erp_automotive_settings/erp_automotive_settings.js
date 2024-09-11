frappe.ui.form.on("ERP automotive settings", {
    refresh: function(frm) {
        frm.set_query("ws_sales_order", function() {
            return {
            };
        });
    }
});