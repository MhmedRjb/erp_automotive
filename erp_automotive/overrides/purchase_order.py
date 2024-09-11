from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder as CustomPurchaseOrder
from frappe import _
import frappe
class CustomPurchaseOrder(CustomPurchaseOrder):
	def on_submit(self):
		super().on_submit()
		self.update_material_request_workflow()
  
	def update_material_request_workflow(self):
		
		for item in self.items:
			if not item.material_request:
				continue

			material_request = frappe.get_doc("Material Request", item.material_request)

			for request_item in material_request.items:
				if not request_item.sales_order:
					continue

				sales_order = frappe.get_doc("Sales Order", request_item.sales_order)
    
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



