# -*- coding: utf-8 -*-

{
    "name": "Landed Costs for TYP",
    "version": "11.0.0.2.0",
    "author": "Vauxoo",
    "category": "Generic Modules/Account",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        # "default_warehouse_from_sale_team",
        # "stock_landed_costs_segmentation",
        "mrp",
        "stock_landed_costs",
        # "base_automation",

    ],
    "demo": [
        # 'demo/pricelist_demo.xml',
        'demo/purchase_order_demo.xml',
        'demo/product_demo.xml',
    ],
    "data": [
        "data/res_groups.xml",
        "data/product_exchange.xml",
        # "data/ir_actions_server.xml",
        "data/base_automation_data.xml",
        "security/ir.model.access.csv",
        "views/stock_landed_costs.xml",
        "views/account_invoice_view.xml",
        "wizards/invoice_from_guides_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
