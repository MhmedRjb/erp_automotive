from erpnext.selling.doctype.sales_order.sales_order import SalesOrder, get_unreserved_qty
from frappe import _
import frappe
from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import (
	validate_stock_reservation_settings,
	get_sre_reserved_qty_details_for_voucher,
	get_available_qty_to_reserve,
)
from frappe.utils import cint, flt, nowdate, nowtime
from typing import Literal

class CustomSalesOrder(SalesOrder):
	def on_submit(self):
		self.create_stock_reservation_entries(self.get("items"), "Purchase Receipt", True)

	def create_stock_reservation_entries(
		self,
		items_details: list[dict] | None = None,
		from_voucher_type: Literal["Pick List", "Purchase Receipt"] = None,
		notify=True,
	) -> None:
		"""Creates Stock Reservation Entries for Sales Order Items."""

		validate_stock_reservation_settings(self)

		allow_partial_reservation = frappe.db.get_single_value("Stock Settings", "allow_partial_reservation")

		items = []
		print("items_details",items_details)
		
		if items_details:
			for item in items_details:
				print(item.get("item"))
				so_item = frappe.get_doc("Sales Order Item", item.get("name"))
				so_item.warehouse = item.get("warehouse")
				so_item.qty_to_reserve = (
					flt(item.get("qty_to_reserve"))
					if from_voucher_type in ["Pick List", "Purchase Receipt"]
					else (
						flt(item.get("qty_to_reserve"))
						* (flt(item.get("conversion_factor")) or flt(so_item.conversion_factor) or 1)
					)
				)
				so_item.from_voucher_no = item.get("from_voucher_no")
				so_item.from_voucher_detail_no = item.get("from_voucher_detail_no")
				so_item.serial_and_batch_bundle = item.get("serial_and_batch_bundle")
				so_item.custom_serial_no_saver =item.get("custom_serial_no_saver")
				items.append(so_item)

		sre_count = 0
		reserved_qty_details = get_sre_reserved_qty_details_for_voucher("Sales Order", self.name)

		for item in items if items_details else self.get("items"):

			if item.get("reserve_stock"):
				continue


			is_stock_item, has_serial_no, has_batch_no = frappe.get_cached_value(
				"Item", item.item_code, ["is_stock_item", "has_serial_no", "has_batch_no"]
			)


			unreserved_qty = get_unreserved_qty(item, reserved_qty_details)

			available_qty_to_reserve = get_available_qty_to_reserve(item.item_code, item.warehouse)

			# No stock available to reserve, notify the user and skip the item.
			qty_to_be_reserved = min(unreserved_qty, available_qty_to_reserve)

			sre = frappe.new_doc("Stock Reservation Entry")

			sre.item_code = item.item_code
			sre.warehouse = item.warehouse
			sre.has_serial_no = has_serial_no
			sre.has_batch_no = has_batch_no
			sre.voucher_type = "Sales Order"
			sre.voucher_no = self.name
			sre.voucher_detail_no = item.name
			sre.available_qty = available_qty_to_reserve
			sre.voucher_qty = item.stock_qty
			sre.reserved_qty = qty_to_be_reserved
			sre.company = self.company
			sre.stock_uom = item.stock_uom
			sre.project = self.project

			if from_voucher_type:
				sre.from_voucher_type = from_voucher_type
				sre.from_voucher_no = item.from_voucher_no
				sre.from_voucher_detail_no = item.from_voucher_detail_no

			if item.get("custom_serial_no_saver"):
				serial_nos = item.custom_serial_no_saver.split('\n')
				sre.reservation_based_on = "Serial and Batch"			
				picked_qty = 0
				for serial_no in serial_nos:
					if serial_no:
						print('if if serial_no if',serial_no)
						sre.append(
							"sb_entries",
							{
								"serial_no": serial_no,
								"batch_no": None,  # Assuming no batch number is provided
								"qty": 1,  # Assuming each serial number represents one unit
								"warehouse": item.warehouse,
							},
						)
						picked_qty += 1
				sre.save()
				sre.submit()
			sre_count += 1

