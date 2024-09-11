from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from frappe import _
import frappe
class CustomPurchaseReceipt(PurchaseReceipt):
    
    def before_save(self):
        for item in self.items:
            if not item.serial_and_batch_bundle and item.serial_no:
                serial_numbers = item.serial_no.split("\n")
                for serial_no in serial_numbers:
                    serial_number_doc = frappe.new_doc('Serial No')
                    serial_number_doc.item_code = item.item_code
                    serial_number_doc.serial_no = serial_no.strip()
                    serial_number_doc.purchase_receipt = self.name
                    serial_number_doc.company = self.company
                    serial_number_doc.purchase_date = self.posting_date
                    serial_number_doc.status = _("without customs card")
                    serial_number_doc.insert()  


#TODO:test the following code and change to it 
    # def before_save(self):
    #     for item in self.items:
    #         if item.serial_no:
    #             serial_nos = item.serial_no.split('\n')
    #             for serial_no in serial_nos:
    #                 if not frappe.db.exists('Serial No', serial_no.strip()):
    #                     doc = frappe.new_doc('Serial No')
    #                     doc.update({
    #                         'item_code': item.item_code,
    #                         'serial_no': serial_no.strip(),
    #                         'purchase_receipt': self.name,
    #                         'company': self.company,
    #                         'purchase_date': self.posting_date,
    #                         'status': _("without customs card")
    #                     })
    #                     doc.insert()        



