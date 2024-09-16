from erpnext.stock.doctype.delivery_note.delivery_note import DeliveryNote
from frappe import _
import frappe
from erp_automotive.utilities.validate import validate_erp_automotive_settings


class CustomDeliveryNote(DeliveryNote):
	def on_submit(self):
		super().on_submit()
		self.update_material_request_workflow()
	
	
	def update_material_request_workflow(self):
		
		for item in self.items:
			if not item.against_sales_order:
				continue

			try:
				sales_order = frappe.get_doc("Sales Order", item.against_sales_order)
			except frappe.exceptions.DoesNotExistError:
				frappe.msgprint(
					_("Sales Order {0} does not exist.").format(frappe.bold(item.against_sales_order)),
					title=_("Sales Order Not Found"),
					indicator="red",
					alert=True
				)
			workflow_state = frappe.db.get_single_value("ERP automotive settings", "ws_salesorder_dn")

			sales_order.db_set("workflow_state", workflow_state)

			frappe.msgprint(
				_("Sales Order {0} has been updated to {1}.").format(
					frappe.bold(sales_order.name), frappe.bold(workflow_state)
				),
				title=_("Sales Order"),
				indicator="orange",
				alert=True
			)

