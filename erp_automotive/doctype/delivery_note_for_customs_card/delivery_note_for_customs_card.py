# Copyright (c) 2024, highsoultion and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe
from frappe import _

class DeliveryNoteforCustomsCard(Document):
	def on_submit(self):
		self.update_customs_card_data()

	def on_cancel(self):
		self.active_last_dn()



	def update_customs_card_data(self):
		customs_card = frappe.get_doc(
			"customs card", self.customs_card)
		customs_card.date= self.date
		customs_card.previous_holder = customs_card.current_holder
		customs_card.current_holder = self.party_name
		customs_card.status = "Delivered"
		customs_card.save()

	def active_last_dn(self):
		last_dn=frappe.db.get_all("Delivery Note for Customs Card",
								 fields=["customs_card","party_name","holder_now"],
								 filters={"customs_card":self.customs_card,"docstatus":1},
								 order_by="creation desc",
								 )[0]
		
		customs_card = frappe.get_doc(
			"customs card", self.customs_card)
		
		customs_card.date= last_dn.date
		customs_card.previous_holder = last_dn.party_name
		customs_card.current_holder = last_dn.holder_now
		customs_card.save()

def get_customs_card_owner(custome_card):
	return frappe.db.get_value("customs card", custome_card, "current_holder")
