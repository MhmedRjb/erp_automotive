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
		# self.update_reserved_with_seril_sales_order()

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

			for po_item in purchase_order.items:
				if not po_item.material_request:
					continue

				try:
					material_request = frappe.get_doc("Material Request", po_item.material_request)
				except frappe.exceptions.DoesNotExistError:
					frappe.msgprint(
						_("Material Request {0} does not exist.").format(frappe.bold(po_item.material_request)),
						title=_("Material Request Not Found"),
						indicator="red",
						alert=True
					)
					continue
				except Exception as e:
					frappe.log_error(message=str(e), title="Error fetching Material Request")
					frappe.msgprint(
						_("An error occurred while fetching Material Request {0}.").format(frappe.bold(po_item.material_request)),
						title=_("Error"),
						indicator="red",
						alert=True
					)
					continue

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
					except Exception as e:
						frappe.log_error(message=str(e), title="Error fetching Sales Order")
						frappe.msgprint(
							_("An error occurred while fetching Sales Order {0}.").format(frappe.bold(request_item.sales_order)),
							title=_("Error"),
							indicator="red",
							alert=True
						)
						continue

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
	 
	def update_reserved_with_sn_from_sales_order(self):
		#bring the serial numbers from items in the purchase receipt and update the reserved  that have the same sales order
		for item in self.items:
			if not item.serial_no:
				continue
			serial_numbers = item.serial_no.split("\n")
			for serial_no in serial_numbers:
				serial_no_doc = frappe.get_doc("Serial No", serial_no)
				serial_no_doc.reserved = 1
				serial_no_doc.save()
				frappe.db.commit()
				frappe.msgprint(
					_("Serial No {0} has been updated to reserved").format(frappe.bold(serial_no)),
					title=_("Serial No"),
					indicator="green",
					alert=True
				)
