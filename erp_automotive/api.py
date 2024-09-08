import frappe
from frappe import _

@frappe.whitelist()
def templet_list(item_group, templet=None, category=None, model=None, colour=None, colour2=None, item=None):
    attribute_query = """
        SELECT DISTINCT attribute
        FROM `tabItem Variant Attribute`order by `attribute`
    """
    attributes = frappe.db.sql(attribute_query, as_list=1)
    
    attribute_map = {f'attr_{i}': attr[0] for i, attr in enumerate(attributes)}

    select_clauses = [
        "t1.name AS parent",
        "t1.item_group",
        f"MAX(CASE WHEN t2.attribute = '{attribute_map.get('attr_3')}' THEN t2.attribute_value ELSE NULL END) AS model",
        f"MAX(CASE WHEN t2.attribute = '{attribute_map.get('attr_0')}' THEN t2.attribute_value ELSE NULL END) AS category",
        f"MAX(CASE WHEN t2.attribute = '{attribute_map.get('attr_2')}' THEN t2.attribute_value ELSE NULL END) AS templet",
        f"MAX(CASE WHEN t2.attribute = '{attribute_map.get('attr_1')}' THEN t2.attribute_value ELSE NULL END) AS colour",
        "t3.name AS variant_of",
        f"MAX(CASE WHEN t2.attribute = '{attribute_map.get('attr_2')}' THEN t2.attribute_value ELSE NULL END) AS colour2"
    ]

    query = f"""
        SELECT DISTINCT
            {', '.join(select_clauses)}
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
    items = frappe.db.sql(query, item_group, as_list=1)

    filters = [
        (templet, 6),
        (category, 3),
        (model, 2),
        (colour, 5),
        (colour2, 7),
        (item, 0)
    ]

    def get_unique_values(items, attribute_index):
        return list(set(item[attribute_index] for item in items if item[attribute_index] is not None))

    def filter_items(items, attribute_index, attribute_value):
        return [item for item in items if item[attribute_index] == attribute_value]

    for attribute_value, attribute_index in filters:
        if attribute_value is None:
            return get_unique_values(items, attribute_index)
        items = filter_items(items, attribute_index, attribute_value)

    return items