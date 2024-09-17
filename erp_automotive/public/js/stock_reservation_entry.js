frappe.ui.form.on('Stock Reservation Entry', {
	refresh(frm) {
		
	}
});

frappe.ui.form.on('Stock Reservation Entry',  {
    refresh: function(frm) {
        frm.set_query("serial_no", "sb_entries", function (doc, cdt, cdn) {
			var selected_serial_nos = doc.sb_entries.map((row) => {
				return row.serial_no;
			});
			var row = locals[cdt][cdn];
          return {
            "filters": {
				item_code: doc.item_code,
				warehouse: row.warehouse,
				status: "Active",
				name: ["not in", selected_serial_nos],
				custom_reservation_status:"unReserved",
            },
          };
        });
    }
});
