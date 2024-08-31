import frappe
from frappe import _

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
	
# @frappe.whitelist()
# def filter_by_item_group(item_group):
# 	query = """
# 		SELECT distinct
# 			t1.name AS parent,
# 			t1.item_group,
# 			MAX(CASE WHEN t2.attribute = 'model' THEN t2.attribute_value ELSE NULL END) AS model,
# 			MAX(CASE WHEN t2.attribute = 'category' THEN t2.attribute_value ELSE NULL END) AS category,
# 			MAX(CASE WHEN t2.attribute = 'type' THEN t2.attribute_value ELSE NULL END) AS type,
# 			MAX(CASE WHEN t2.attribute = 'Colour' THEN t2.attribute_value ELSE NULL END) AS colour
# 		FROM 
# 			`tabItem` t1
# 		LEFT JOIN 
# 			`tabItem Variant Attribute` t2 ON t1.name = t2.parent
# 		WHERE 
# 			t1.item_group = %s
# 		GROUP BY 
# 			t1.name, t1.item_group
# 	"""
# 	print(query)
# 	results = frappe.db.sql(query, item_group, as_list=1)
# 	return results


@frappe.whitelist()
def type_list(item_group, type=None, category=None, model=None, colour=None, item=None):
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
            t1.item_group = %s and t1.disabled = 0 
        GROUP BY 
            t1.name, t1.item_group
    """
    print("Executing query:", query)
    results = frappe.db.sql(query, item_group, as_list=1)
    print("Query results:", results)

    items = results

    if type is None:
        type_list = list(set(item[4] for item in items if item[4] is not None))
        print("Distinct types:", type_list)
        return type_list

    filtered_items = [item for item in items if item[4] == type]

    if category is None:
        category_list = list(set(item[3] for item in filtered_items if item[3] is not None))
        print("Distinct categories:", category_list)
        return category_list

    filtered_items = [item for item in filtered_items if item[3] == category]

    if model is None:
        model_list = list(set(item[2] for item in filtered_items if item[2] is not None))
        print("Distinct models:", model_list)
        return model_list

    filtered_items = [item for item in filtered_items if item[2] == model]

    if colour is None:
        colour_list = list(set(item[5] for item in filtered_items if item[5] is not None))
        print("Distinct colours:", colour_list)
        return colour_list

    filtered_items = [item for item in filtered_items if item[5] == colour]

    if item is None:
        item_list = list(set(item[0] for item in filtered_items if item[0] is not None))
        print("Distinct items:", item_list)
        #make it value without list
        item_list = item_list[0]
        return item_list

    filtered_items = [item for item in filtered_items if item[0] == item]

    return filtered_items

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
