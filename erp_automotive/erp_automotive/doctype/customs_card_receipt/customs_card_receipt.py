# Copyright (c) 2024, highsoultion and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _
from frappe.utils import get_url_to_form
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
			customs_card={
				"customs_card_number":item.customs_card,
				"customs_card_date":self.date,
				"iamge":item.custom_image,
				"serial_no":item.serial_no,
			}
			cc.update(customs_card)
			item_attributes = frappe.get_all(
			"Item Variant Attribute",
			fields=["attribute", "attribute_value"],
			filters={
				"parent": item.item_code  
			},
			order_by="idx"
			)

			for attribute in item_attributes:
				cc.append("item_variant_attribute", {
					"attribute": attribute.attribute,
					"attribute_value": attribute.attribute_value
				})
			cc.save()
			cc.submit()
			frappe.db.commit()
			customs_card_link = get_url_to_form("Customs Card", item.customs_card)
			frappe.msgprint(
				_("Customs Card {0} is created").format(f'<a href="{customs_card_link}">{frappe.bold(item.customs_card)}</a>'),
				title=_("Customs Card"),
				indicator="green",
				alert=True
			)
			

	def before_cancel(self):
		for item in self.items:
			frappe.db.set_value("Serial No", item.serial_no, "customs_card", "get deleted")

