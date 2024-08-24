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
		print(self.get("items"))
		#print items
		for item in self.get("items"):
			print(item.get("item_code"))
			print(item.get("qty_to_reserve"))
			print(item.get("warehouse"))
			print(item.get("from_voucher_no"))
			print(item.get("from_voucher_detail_no"))
			print(item.get("custom_serial_no_saver"))
			print(item.get("reserve_stock"))


		# print("on_submit")
		# # self.create_stock_reservation_entries(items_details=self.get("items"), from_voucher_type="Sales Order")
		# print("validate")
		# print("/m/n\m\m\m\n\n")
		# print("")

	# Call the create_stock_reservation_entries method defined in the class
		self.create_stock_reservation_entries(self.get("items"), "Purchase Receipt", True)

	def create_stock_reservation_entries(
		self,
		items_details: list[dict] | None = None,
		from_voucher_type: Literal["Pick List", "Purchase Receipt"] = None,
		notify=True,
	) -> None:
		"""Creates Stock Reservation Entries for Sales Order Items."""

		if not from_voucher_type and (
			self.get("_action") == "submit"
			and self.set_warehouse
			and cint(frappe.get_cached_value("Warehouse", self.set_warehouse, "is_group"))
		):
			return frappe.msgprint(
				_("Stock cannot be reserved in the group warehouse {0}.").format(
					frappe.bold(self.set_warehouse)
				)
			)

		# Add the rest of the logic for creating stock reservation entries here
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
				print("so_item.custom_serial_no_saver",so_item.custom_serial_no_saver)
				print("so_item.custom_serial_no_saver",so_item)
				items.append(so_item)

		sre_count = 0
		reserved_qty_details = get_sre_reserved_qty_details_for_voucher("Sales Order", self.name)

		for item in items if items_details else self.get("items"):
			# Skip if `Reserved Stock` is not checked for the item.
			print("0000111\n\n\n")
			print("000111\n\n\n")

			if item.get("reserve_stock"):
				print("109")
				continue

			# Stock should be reserved from the Pick List if has Picked Qty.
			if not from_voucher_type == "Pick List" and flt(item.picked_qty) > 0:
				frappe.throw(
					_("Row #{0}: Item {1} has been picked, please reserve stock from the Pick List.").format(
						item.idx, frappe.bold(item.item_code)
					)
				)

			is_stock_item, has_serial_no, has_batch_no = frappe.get_cached_value(
				"Item", item.item_code, ["is_stock_item", "has_serial_no", "has_batch_no"]
			)

			# Skip if Non-Stock Item.
			if not is_stock_item:
				print("125")
				if not from_voucher_type:
					frappe.msgprint(
						_("Row #{0}: Stock cannot be reserved for a non-stock Item {1}").format(
							item.idx, frappe.bold(item.item_code)
						),
						title=_("Stock Reservation"),
						indicator="yellow",
					)

				item.db_set("reserve_stock", 0)
				continue

			# Skip if Group Warehouse.
			if frappe.get_cached_value("Warehouse", item.warehouse, "is_group"):
				print("139")
				frappe.msgprint(
					_("Row #{0}: Stock cannot be reserved in group warehouse {1}.").format(
						item.idx, frappe.bold(item.warehouse)
					),
					title=_("Stock Reservation"),
					indicator="yellow",
				)
				continue

			unreserved_qty = get_unreserved_qty(item, reserved_qty_details)

			# Stock is already reserved for the item, notify the user and skip the item.
			if unreserved_qty <= 0:
				if not from_voucher_type:
					frappe.msgprint(
						_("Row #{0}: Stock is already reserved for the Item {1}.").format(
							item.idx, frappe.bold(item.item_code)
						),
						title=_("Stock Reservation"),
						indicator="yellow",
					)

				continue

			available_qty_to_reserve = get_available_qty_to_reserve(item.item_code, item.warehouse)

			# No stock available to reserve, notify the user and skip the item.
			if available_qty_to_reserve <= 0:
				frappe.msgprint(
					_("Row #{0}: Stock not available to reserve for the Item {1} in Warehouse {2}.").format(
						item.idx, frappe.bold(item.item_code), frappe.bold(item.warehouse)
					),
					title=_("Stock Reservation"),
					indicator="orange",
				)
				continue

			# The quantity which can be reserved.
			qty_to_be_reserved = min(unreserved_qty, available_qty_to_reserve)

			if hasattr(item, "qty_to_reserve"):
				if item.qty_to_reserve <= 0:
					print("181")
					frappe.msgprint(
						_("Row #{0}: Quantity to reserve for the Item {1} should be greater than 0.").format(
							item.idx, frappe.bold(item.item_code)
						),
						title=_("Stock Reservation"),
						indicator="orange",
					)
					continue
				else:
					qty_to_be_reserved = min(qty_to_be_reserved, item.qty_to_reserve)

			# Partial Reservation
			if qty_to_be_reserved < unreserved_qty:
				print("194")
				if not from_voucher_type and (
					not item.get("qty_to_reserve") or qty_to_be_reserved < flt(item.get("qty_to_reserve"))
				):
					msg = _("Row #{0}: Only {1} available to reserve for the Item {2}").format(
						item.idx,
						frappe.bold(str(qty_to_be_reserved / item.conversion_factor) + " " + item.uom),
						frappe.bold(item.item_code),
					)
					frappe.msgprint(msg, title=_("Stock Reservation"), indicator="orange")

				# Skip the item if `Partial Reservation` is disabled in the Stock Settings.
				if not allow_partial_reservation:
					if qty_to_be_reserved == flt(item.get("qty_to_reserve")):
						msg = _(
							"Enable Allow Partial Reservation in the Stock Settings to reserve partial stock."
						)
						frappe.msgprint(msg, title=_("Partial Stock Reservation"), indicator="yellow")

					continue
			print("1111\n\n\n")
			print(item)
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
				print("from_voucher_type")

			print("222\n\n\n")
			print(item.custom_serial_no_saver)


			if item.get("custom_serial_no_saver"):
				serial_nos = item.custom_serial_no_saver.split('\n')
				sre.reservation_based_on = "Serial and Batch"
				print("249")
				print(serial_nos)
			
				picked_qty = 0
				for serial_no in serial_nos:
					print("254")
					print("serial_no",serial_no)
					# if picked_qty >= qty_to_be_reserved:
					#     break
					# serial_no = serial_no.strip()
					if serial_no:
						print('if if serial_no if',serial_no)
						sre.append(
							"sb_entries",
							{
								"serial_no": "ABC-081",
								"batch_no": None,  # Assuming no batch number is provided
								"qty": 1,  # Assuming each serial number represents one unit
								"warehouse": item.warehouse,
							},
						)
						picked_qty += 1
						print("sre.sb_entries",sre.sb_entries)
						print(picked_qty)
				print("2323\n\n\n")
				print(item)
			
				sre.save()
				sre.submit()
			sre_count += 1

		if sre_count and notify:
			print("282")
			frappe.msgprint(_("Stock Reservation Entries Created"), alert=True, indicator="green")







# create_stock_reservation_entries(self,items_details=items_details, from_voucher_type=from_voucher_type,notify=notify,)


# create_stock_reservation_entries(self,items_details=items_details, from_voucher_type=from_voucher_type,notify=notify,)
