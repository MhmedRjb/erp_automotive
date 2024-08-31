import frappe
from frappe import _
from frappe.utils import flt, cint, cstr
from erpnext.stock.doctype.item.item import get_item_defaults

# @frappe.whitelist()
# def get_items(attribute):
# 	result = frappe.db.sql(
# 		"""SELECT DISTINCT attribute_value from `tabItem Variant Attribute` where attribute = %s""",
# 		attribute,
# 		as_list=1
# 	)
# 	# Flatten the list of lists
# 	flat_result = [item[0] for item in result if item[0] is not None]
# 	return flat_result


# def get_item_from_group(group):
#     result = frappe.db.sql(
#         """SELECT name from `tabItem` where item_group = %s""",
#         group,
#         as_list=1
#     )
#     # Flatten the list of lists
#     flat_result = [item[0] for item in result if item[0] is not None]
#     return flat_result


# @frappe.whitelist()
# def get_item_type(item_group):
# 	# Fetch item names based on the item group
# 	items = frappe.db.sql(
# 		"""SELECT name FROM `tabItem` WHERE item_group = %s""",
# 		item_group,
# 		as_list=1
# 	)
# 	item_list = [item[0] for item in items if item[0] is not None]

# 	if not item_list:
# 		return []

# 	# Fetch distinct model attribute values for the fetched items
# 	result = frappe.db.sql(
# 		"""SELECT DISTINCT attribute_value FROM `tabItem Variant Attribute` WHERE attribute = 'type' AND parent IN %s""",
# 		(tuple(item_list),),
# 		as_list=1
# 	)
# 	type_list = [item[0] for item in result if item[0] is not None]

# 	return type_list

# @frappe.whitelist()
# def get_item_category(item_group,item_type):
# 	# Fetch item names based on the item group
# 	items = frappe.db.sql(
# 		"""SELECT name FROM `tabItem` WHERE item_group = %s""",
# 		item_group,
# 		as_list=1
# 	)
# 	item_list = [item[0] for item in items if item[0] is not None]

# 	if not item_list:
# 		return []

# 	# Fetch distinct model attribute values for the fetched items
# 	result = frappe.db.sql(
# 		"""SELECT DISTINCT attribute_value FROM `tabItem Variant Attribute` WHERE attribute = 'category' AND parent IN %s""",
# 		(tuple(item_list),),
# 		as_list=1
# 	)
# 	category_list = [item[0] for item in result if item[0] is not None]

# 	return category_list
	
@frappe.whitelist()
def filter_by_item_group(item_group):
	query = """
		SELECT distinct
			t1.name AS parent,
			t1.item_group,
			MAX(CASE WHEN t2.attribute = 'model' THEN t2.attribute_value ELSE NULL END) AS model,
			MAX(CASE WHEN t2.attribute = 'category' THEN t2.attribute_value ELSE NULL END) AS category,
			MAX(CASE WHEN t2.attribute = 'type' THEN t2.attribute_value ELSE NULL END) AS type,
			MAX(CASE WHEN t2.attribute = 'Colour' THEN t2.attribute_value ELSE NULL END) AS colour
		FROM 
			`tabItem` t1
		LEFT JOIN 
			`tabItem Variant Attribute` t2 ON t1.name = t2.parent
		WHERE 
			t1.item_group = %s
		GROUP BY 
			t1.name, t1.item_group
	"""
	results = frappe.db.sql(query, item_group, as_list=1)
	type_list = [item[2] for item in results if item[0] is not None]

	return results


@frappe.whitelist()
def type_list(item_group, type=None, category=None,model=None,colour=None):
	items = filter_by_item_group(item_group)
	if type is None:
		type_list = list(set(item[4] for item in items if item[0] is not None))
		return type_list
	elif category is None:
		category_list = list(set(item[3] for item in items if item[0] is not None))
		return category_list
	elif model is None:
		model_list = list(set(item[2] for item in items if item[0] is not None))
		return model_list
	elif colour is None:
		colour_list = list(set(item[5] for item in items if item[0] is not None))
		return colour_list
	

# @frappe.whitelist()
# def category_list(item_group, custom_type):
# 	items = filter_by_custom_type(item_group, custom_type)
# 	category_list = list(set(item[3] for item in items if item[0] is not None))
# 	return category_list


# def filter_by_custom_type(item_group, custom_type):
# 	items = filter_by_item_group(item_group)
# 	return [item for item in items if item['type'] == custom_type]

# def filter_by_custom_category(item_group, custom_type, custom_category):
# 	items = filter_by_custom_type(item_group, custom_type)
# 	return [item for item in items if item['category'] == custom_category]
