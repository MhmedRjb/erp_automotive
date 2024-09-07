import frappe
from frappe.query_builder import DocType
from frappe.utils import now_datetime, add_days
from datetime import datetime, timedelta

def schedule_update():
	nuumber_of_days=frappe.db.get_value("ERP automotive settings", None, ["days_after_cancel_reservation"])

	date = (datetime.now() - timedelta(days=nuumber_of_days)).date()

	sre = frappe.get_all("Stock Reservation Entry", filters={"status": "Reserved",
																"docstatus":1,
																"creation": ["<", date]
																},
																fields=["name"]
																)
	for d in sre:
		c = frappe.get_doc("Stock Reservation Entry",d['name'])
		c.cancel()
		frappe.db.commit()
		
