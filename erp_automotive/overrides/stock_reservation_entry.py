from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import StockReservationEntry
from frappe import _
import frappe
from erpnext.stock.utils import get_or_make_bin, get_stock_balance
import frappe
from frappe.query_builder import DocType
from frappe.utils import now_datetime, add_days


class CustomStockReservationEntry(StockReservationEntry):
	pass
	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

	def on_submit(self):
		super().on_submit()
		# Update custom_reservation_status to "Reserved"
		for sb in self.sb_entries:
			print(self.item_code, sb.serial_no)
			sn_doc = frappe.get_doc("Serial No", sb.serial_no)
			sn_doc.custom_reservation_status = _("Reserved")
			sn_doc.save()

	def on_cancel(self):
		super().on_cancel()
		# Update custom_reservation_status to "Unreserved"
		for sb in self.sb_entries:
			print(self.item_code, sb.serial_no)
			sn_doc = frappe.get_doc("Serial No", sb.serial_no)
			sn_doc.custom_reservation_status = _("un Reserved")
			sn_doc.save()

	def on_update_after_submit(self):
		old_sb_entries = self.get_doc_before_save().sb_entries
		old_sb_entries = [sb.serial_no for sb in old_sb_entries]
		new_sb_entries = [sb.serial_no for sb in self.sb_entries]
		for sb in old_sb_entries:
			if sb not in new_sb_entries:
				print(self.item_code, sb,"un Reserved")
				sn_doc = frappe.get_doc("Serial No", sb)
				sn_doc.custom_reservation_status = _("un Reserved")
				sn_doc.save()
		for sb in new_sb_entries:
			if sb not in old_sb_entries:
				print(self.item_code, sb,"Reserved")
				sn_doc = frappe.get_doc("Serial No", sb)
				sn_doc.custom_reservation_status = _("Reserved")
				sn_doc.save()



		