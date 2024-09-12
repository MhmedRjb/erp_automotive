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
			cc=frappe.new_doc("customs card")
			cc.customs_card_number=item.customs_card
			cc.customs_card_date=self.date
			cc.iamge=item.custom_image
			item_attributes = frappe.get_all(
			"Item Variant Attribute",
			fields=["attribute", "attribute_value"],
			filters={
				"parent": item.item_code  
			},
			order_by="idx"
			)

			for attribute in item_attributes:
				print(attribute, attribute.attribute, attribute.attribute_value)
			print("===============************================")
			#assign values to custom_item_variant_attribute table	
			for attribute in item_attributes:
				cc.append("item_variant_attribute", {
					"attribute": attribute.attribute,
					"attribute_value": attribute.attribute_value
				})
			cc.save(ignore_permissions=True,ignore_version=True )
			cc.submit()


	def after_cancel(self):
		pass

	def before_cancel(self):
		# print ("before_ cancel")
		# print("===========================\n\n\n========================")
		for item in self.items:
			frappe.db.set_value("Serial No", item.serial_no, "customs_card", "get deleted")

