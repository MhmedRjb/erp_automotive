from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from frappe import _
import frappe
class CustomPurchaseReceipt(PurchaseReceipt):
	
	def before_save(self):
		for item in self.items:
			if not item.serial_and_batch_bundle and item.serial_no:
				serial_numbers = item.serial_no.split("\n")
				for serial_no in serial_numbers:
					serial_number_doc = frappe.new_doc('Serial No')
					serial_number_doc.item_code = item.item_code
					serial_number_doc.serial_no = serial_no.strip()
					serial_number_doc.purchase_receipt = self.name
					serial_number_doc.company = self.company
					serial_number_doc.purchase_date = self.posting_date
					serial_number_doc.insert()  


	def on_submit(self):
		super().on_submit()
		self.update_material_request_workflow()
		
	
	def update_material_request_workflow(self):
		for item in self.items:
			if not item.purchase_order:
				continue
			
			try:
				purchase_order = frappe.get_doc("Purchase Order", item.purchase_order)
			except frappe.exceptions.DoesNotExistError:
				frappe.msgprint(
					_("Purchase Receipt has no Purchase Order and no Material Request."),
					indicator="red",
					alert=True
				)
				return
			
		for item in purchase_order.items:
			if not item.material_request:
				continue

			material_request = frappe.get_doc("Material Request", item.material_request)

			for request_item in material_request.items:
				if not request_item.sales_order:
					continue

				sales_order = frappe.get_doc("Sales Order", request_item.sales_order)
	
				workflow_state = frappe.db.get_single_value("ERP automotive settings", "ws_salesorder_ps")
	
				sales_order.db_set("workflow_state", workflow_state)

				frappe.msgprint(
					_("Sales Order {0} has been updated to {1}.").format(
						frappe.bold(sales_order.name), frappe.bold(workflow_state)
					),
					title=_("Sales Order"),
					indicator="orange",
					alert=True
				)


