from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt

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
                    serial_number_doc.insert()
