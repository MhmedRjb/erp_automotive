import frappe
from frappe import _
from frappe.model.workflow import get_workflow_name

def validate_erp_automotive_settings():
    
    if not get_workflow_name("Sales Order"):
        return

    ws_sales_order= frappe.db.get_single_value("ERP Automotive Settings", "ws_sales_order")
    ws_salesorder_po = frappe.db.get_single_value("ERP Automotive Settings", "ws_salesorder_po")
    ws_salesorder_ps = frappe.db.get_single_value("ERP Automotive Settings", "ws_salesorder_ps")

    if not ws_salesorder_po or not ws_salesorder_ps or not ws_sales_order:
        message = _("be sure there is no empty field in ERP Automotive Settings or disable the workflow")
        frappe.throw(message, title="Sales Order")