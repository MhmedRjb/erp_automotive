from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder as CustomPurchaseOrder
from frappe import _
import frappe
from erp_automotive.utilities.validate import validate_erp_automotive_settings
class CustomPurchaseOrder(CustomPurchaseOrder):
	def on_submit(self):
		super().on_submit()
		self.update_material_request_workflow()
	
	
	def update_material_request_workflow(self):
		
		for item in self.items:
			if not item.material_request:
				continue

			try:
				material_request = frappe.get_doc("Material Request", item.material_request)
			except frappe.exceptions.DoesNotExistError:
				frappe.msgprint(
					_("Material Request {0} does not exist.").format(frappe.bold(item.material_request)),
					title=_("Material Request Not Found"),
					indicator="red",
					alert=True
				)
				
			for request_item in material_request.items:
				if not request_item.sales_order:
					continue
				try:
					sales_order = frappe.get_doc("Sales Order", request_item.sales_order)
				except frappe.exceptions.DoesNotExistError:
					frappe.msgprint(
						_("Sales Order {0} does not exist.").format(frappe.bold(request_item.sales_order)),
						title=_("Sales Order Not Found"),
						indicator="red",
						alert=True
					)
					continue
				workflow_state = frappe.db.get_single_value("ERP automotive settings", "ws_salesorder_po")
	
				sales_order.db_set("workflow_state", workflow_state)

				frappe.msgprint(
					_("Sales Order {0} has been updated to {1}.").format(
						frappe.bold(sales_order.name), frappe.bold(workflow_state)
					),
					title=_("Sales Order"),
					indicator="orange",
					alert=True
				)



