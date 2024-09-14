from frappe.model.document import Document
from frappe import _
import frappe

class customscard(Document):
    def on_submit(self):
        self.update_serial_no_data()
  
    def on_update(self):
        self.update_serial_no_data()
  
    def on_update_after_submit(self):
        self.update_serial_no_data()
  
    def update_serial_no_data(self):
        serial_no = frappe.db.get_value("Serial No", {"customs_card": self.name}, "name")
        
        if serial_no:
            
            frappe.db.set_value("Serial No", serial_no, {
                "custom_previous_holder": self.previous_holder,
                "custom_received_date": self.date,
                "custom_current_holder": self.current_holder
            })
            
            frappe.msgprint(
                _("Serial No {0} updated successfully.").format(frappe.bold(serial_no)),
                title=_("Update Successful"),
                indicator="green",
                alert=True
            )
        else:
            frappe.msgprint(
                _("No Serial No found with Customs Card {0}.").format(frappe.bold(self.name)),
                title=_("Update Failed"),
                indicator="red",
                alert=True
            )