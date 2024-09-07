import frappe
from frappe import _


@frappe.whitelist()
def templet_list(item_group, templet=None, category=None, model=None, colour=None, item=None):
	
	
	conditiones= ""
	
	query = f"""
			SELECT DISTINCT
				t1.name AS parent,
				t1.item_group,
				MAX(CASE WHEN t2.attribute = 'model' THEN t2.attribute_value ELSE NULL END) AS model,
				MAX(CASE WHEN t2.attribute = 'category' THEN t2.attribute_value ELSE NULL END) AS category,
				MAX(CASE WHEN t2.attribute = 'templet' THEN t2.attribute_value ELSE NULL END) AS templet,
				MAX(CASE WHEN t2.attribute = 'Colour' THEN t2.attribute_value ELSE NULL END) AS colour,
				t3.name AS variant_of
			FROM 
				`tabItem` t1
			LEFT JOIN 
				`tabItem Variant Attribute` t2 ON t1.name = t2.parent
			LEFT JOIN 
				`tabItem` t3 ON t1.variant_of = t3.name
			WHERE 
				t1.item_group = %s 
				AND t1.disabled = 0 
			GROUP BY 
				t1.name, t1.item_group, t3.name
	"""
	results = frappe.db.sql(query, item_group, as_list=1)

	items = results

	if templet is None:
		t_l = list(set(item[6] for item in items if item[6] is not None))	
		return t_l ,items

	filtered_items = [item for item in items if item[6] == templet] 
	if category is None:
		category_list = list(set(item[3] for item in filtered_items if item[3] is not None))
		return category_list ,items

	filtered_items = [item for item in filtered_items if item[3] == category]

	if model is None:
		model_list = list(set(item[2] for item in filtered_items if item[2] is not None))
		return model_list,1

	filtered_items = [item for item in filtered_items if item[2] == model]

	if colour is None:
		colour_list = list(set(item[5] for item in filtered_items if item[5] is not None))
		return colour_list,1

	filtered_items = [item for item in filtered_items if item[5] == colour]

	if item is None:
		item_list = list(set(item[0] for item in filtered_items if item[0] is not None))
		if item_list:  # Check if item_list is not empty
			item_list = item_list[0]
		return item_list,1

	filtered_items = [item for item in filtered_items if item[0] == item]
	return filtered_items



@frappe.whitelist()
def get_item_and_serial_no(item_group, templet=None, category=None, model=None, colour=None, item=None):
	t_l,items=templet_list(item_group,templet='test')
	print(t_l)	
	print(items)
	all_items = [item[0] for item in items if item[0] is not None]
	print(all_items)
	sn = frappe.db.get_list('Serial No', filters={'item_code': ['in', all_items]}, fields=['name', 'item_code'])
	print(sn)
	
	return sn