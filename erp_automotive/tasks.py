import frappe
from frappe.query_builder import DocType
from frappe.utils import now_datetime, add_days
from datetime import datetime, timedelta

def schedule_update():
	# date = add_days(now_datetime(),-1)
	date = (datetime.now() - timedelta(days=2)).date()
	sre = frappe.get_all("Stock Reservation Entry", filters={"status": "Reserved","docstatus":1,"creation": ["<", date]}, fields=["name"])
	for d in sre:
		print(d['name'])
		c = frappe.get_doc("Stock Reservation Entry",d['name'])
		c.cancel()
		frappe.db.commit()
		


	# sre = DocType("Stock Reservation Entry")
	
	# two_days_ago = add_days(now_datetime(),0)
