# Copyright (c) 2024, highsoultion and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class customscardreceipt(Document):
	

	
	def validate(self):
		for item in self.items:
			if not frappe.db.exists("Serial No", item.serial_no):
				frappe.throw(f"Serial No {item.serial_no} does not exist")

		for item in self.items:
			if not item.customs_card:
				frappe.throw(f"Customs Card {item.serial_no} does not exist")	
				
	def on_submit(self):
		for item in self.items:
			frappe.db.set_value("Serial No", item.serial_no, "customs_card", item.customs_card)