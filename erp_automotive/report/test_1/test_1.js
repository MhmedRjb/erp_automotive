// Copyright (c) 2024, highsoultion and contributors
// For license information, please see license.txt
async function fetchAndSetOptions(fieldname, args) {
    try {
        let response = await frappe.call({
            method: 'erp_automotive.api.templet_list',
            args: args
        });
        let itemNames = response.message;

        let filter = frappe.query_report.get_filter(fieldname);
        if (filter) {
            filter.df.options = itemNames.join('\n');
            filter.df.hidden = 0; 
            
            filter.set_value('');
            filter.refresh();
        } else {
            console.error(`${fieldname} filter is not defined`);
        }
    } catch (error) {
        console.error('Error fetching options:', error);
    }
}

function resetDependentFields(fields) {
    fields.forEach((fieldname, index) => {
        let filter = frappe.query_report.get_filter(fieldname);
        if (filter) {
            filter.set_value('');
            if (index > 0) {
                filter.df.hidden = 1;
            }    
            filter.refresh();
        }
    });
}

frappe.query_reports["test_1"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            width: "80",
            options: "Company",
            default: frappe.defaults.get_default("company"),
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            width: "80",
            reqd: 1,
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            width: "80",
            reqd: 1,
            default: frappe.datetime.get_today(),
        },
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            width: "80",
            options: "Item Group",
            change: async function() {        
                const item_group = frappe.query_report.get_filter_value('item_group');
                resetDependentFields(['type', 'category', 'model', 'colour', 'colour2']);
                if (item_group) {
                    await fetchAndSetOptions('type', { item_group: item_group });
                }
            }
        },
        {
            fieldname: "type",
            label: __("Type"),
            fieldtype: "Select",
            width: "80",
            options: [], 
            hidden: 1, 
            change: async function() {
                const item_group = frappe.query_report.get_filter_value('item_group');
                const type = frappe.query_report.get_filter_value('type');
                resetDependentFields(['category', 'model', 'colour', 'colour2']);
                if (item_group && type) {
                    await fetchAndSetOptions('category', { item_group: item_group, templet: type });
                }
            }
        },
        {
            fieldname: "category",
            label: __("Category"),
            fieldtype: "Select",
            width: "80",
            hidden: 1, 
            options: [], 
            change: async function() {
                const item_group = frappe.query_report.get_filter_value('item_group');
                const type = frappe.query_report.get_filter_value('type');
                const category = frappe.query_report.get_filter_value('category');
                resetDependentFields(['model', 'colour', 'colour2']);
                if (item_group && type && category) {
                    await fetchAndSetOptions('model', { item_group: item_group, templet: type, category: category });
                }
            }
        },
        {
            fieldname: "model",
            label: __("Model"),
            fieldtype: "Select",
            width: "80",
            hidden: 1,    
            options: [],
            change: async function() {
                const item_group = frappe.query_report.get_filter_value('item_group');
                const type = frappe.query_report.get_filter_value('type');
                const category = frappe.query_report.get_filter_value('category');
                const model = frappe.query_report.get_filter_value('model');
                resetDependentFields(['colour', 'colour2']);
                if (item_group && type && category && model) {
                    await fetchAndSetOptions('colour', { item_group: item_group, templet: type, category: category, model: model });
                }
            }
        },
        {
            fieldname: "colour",
            label: __("Colour"),
            fieldtype: "Select",
            width: "80",
            hidden: 1,
            options: [],
            change: async function() {
                const item_group = frappe.query_report.get_filter_value('item_group');
                const type = frappe.query_report.get_filter_value('type');
                const category = frappe.query_report.get_filter_value('category');
                const model = frappe.query_report.get_filter_value('model');
                const colour = frappe.query_report.get_filter_value('colour');
                resetDependentFields(['colour2']);
                if (item_group && type && category && model && colour) {
                    await fetchAndSetOptions('colour2', { item_group: item_group, templet: type, category: category, model: model, colour: colour });
                }
            }
        },
        {
            fieldname: "colour2",
            label: __("Colour2"),
            fieldtype: "Select",
            width: "80",
            hidden: 1,
            options: [],
            change: async function() {
                frappe.query_report.refresh();
            }
        },
        {
            fieldname: "item_code",
            label: __("Item"),
            fieldtype: "Link",
            width: "80",
            options: "Item",
            get_query: function () {
                let item_group = frappe.query_report.get_filter_value("item_group");
                return {
                    query: "erpnext.controllers.queries.item_query",
                    filters: {
                        ...(item_group && { item_group }),
                    }
                };
            },
        },
        {
            fieldname: "warehouse",
            label: __("Warehouse"),
            fieldtype: "Link",
            width: "80",
            options: "Warehouse",
            get_query: () => {
                let warehouse_type = frappe.query_report.get_filter_value("warehouse_type");
                let company = frappe.query_report.get_filter_value("company");

                return {
                    filters: {
                        ...(warehouse_type && { warehouse_type }),
                        ...(company && { company }),
                    },
                };
            },
        },
        {
            fieldname: "warehouse_type",
            label: __("Warehouse Type"),
            fieldtype: "Link",
            width: "80",
            options: "Warehouse Type",
        },
        {
            fieldname: "valuation_field_type",
            label: __("Valuation Field Type"),
            fieldtype: "Select",
            width: "80",
            options: "Currency\nFloat",
            default: "Currency",
        },
        {
            fieldname: "include_uom",
            label: __("Include UOM"),
            fieldtype: "Link",
            options: "UOM",
			hidden:1

        },
        {
            fieldname: "show_variant_attributes",
            label: __("Show Variant Attributes"),
            fieldtype: "Check",
			hidden:1
        },
        {
            fieldname: "show_stock_ageing_data",
            label: __("Show Stock Ageing Data"),
            fieldtype: "Check",
			hidden:1

        },
        {
            fieldname: "ignore_closing_balance",
            label: __("Ignore Closing Balance"),
            fieldtype: "Check",
            default: 0,
			hidden:1

        },
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
            value = "<span style='color:red'>" + value + "</span>";
        } else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
            value = "<span style='color:green'>" + value + "</span>";
        }

        return value;
    },
};