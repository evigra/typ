# -*- coding: utf-8 -*-

{
    "name": "Landed Costs for TYP",
    "version": "8.0.0.0.1",
    "author": "Vauxoo",
    "category": "Generic Modules/Account",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "stock_landed_costs_segmentation",
    ],
    "demo": [
    ],
    "data": [
        "data/res_groups.xml",
        "security/ir.model.access.csv",
        "views/stock_landed_costs.xml",
        "wizards/invoice_from_guides_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
