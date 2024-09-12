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
from frappe.model.workflow import get_workflow_name
class CustomSalesOrder(SalesOrder):
	def on_submit(self):

		super().on_submit()
		
		self.test(self.get("items"), "Purchase Receipt", True)
		
	
	def test(
		self,
		items_details: list[dict] | None = None,
		from_voucher_type: Literal["Pick List", "Purchase Receipt"] = None,
		notify=True,
	) -> None:
		"""Creates Stock Reservation Entries for Sales Order Items."""

		validate_stock_reservation_settings(self)


		items = []
		
		if items_details:
			for item in items_details  :
				so_item = frappe.get_doc("Sales Order Item", item.get("name"))
				if item.get("custom_serial_no_saver"):
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


			is_stock_item, has_serial_no, has_batch_no = frappe.get_cached_value(
				"Item", item.item_code, ["is_stock_item", "has_serial_no", "has_batch_no"]
			)


			unreserved_qty = get_unreserved_qty(item, reserved_qty_details)

			available_qty_to_reserve = get_available_qty_to_reserve(item.item_code, item.warehouse)

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


	def after_insert(self):
		self.alert_message()


	def alert_message(self) -> None:
		items_to_request = []
		for item in self.get("items"):
			available_qty_to_reserve = get_available_qty_to_reserve(item.item_code, item.warehouse)
			if available_qty_to_reserve <= 0:
				items_to_request.append({
											"item_code": item.item_code,
											"qty": item.qty,
											"schedule_date": self.delivery_date,
											"warehouse": self.set_warehouse,
											"sales_order": self.name
										})
				frappe.msgprint(
								_("Row #{0}: Stock not available to reserve for the Item {1} in Warehouse {2}.").format(
									item.idx, frappe.bold(item.item_code), frappe.bold(item.warehouse)
								),
								title=_("Stock Reservation"),
								indicator="red",
								alert=True
							)


		if items_to_request:
			workflow_state = frappe.db.get_single_value("ERP automotive settings", "ws_sales_order")
			self.db_set("workflow_state", workflow_state)
		
			material_request = {
				"doctype": "Material Request",
				"material_request_type": "Purchase",
				"items": items_to_request,
			}
			mr = frappe.new_doc("Material Request")
			mr.update(material_request)
			mr.save()
			mr.submit()
			frappe.db.commit()
			for item in self.get("items"):
				if item.item_code in [i["item_code"] for i in items_to_request]:
					item.material_request = mr.name


			frappe.msgprint(
				_("Material Request {0} has been created for the Item {1}.").format(
					frappe.bold(mr.name), frappe.bold(item.item_code)
				),
				title=_("Material Request"),
				indicator="grean",
				alert=True,
			)
			frappe.msgprint(
				_("Sales Order {0} has been connected to {1}.").format(
					frappe.bold(mr.name), frappe.bold(self.name)
				),
				title=_("Sales Order"),
				indicator="orange",
				alert=True,
			)



 
	def validate(self):
		super().validate()

		workflow_name = get_workflow_name("Sales Order")
		if not workflow_name:
			return
		#check if it active 
		ws_salesorder_po = frappe.db.get_single_value("ERP Automotive Settings", "ws_salesorder_po")
		ws_salesorder_ps = frappe.db.get_single_value("ERP Automotive Settings", "ws_salesorder_ps")
		if not ws_salesorder_po or not ws_salesorder_ps:
			# Handle the error message
			message = _("ws_salesorder_po and ws_salesorder_ps in ERP Automotive Settings can't not be empty")
			frappe.throw(message, title="Sales Order")
