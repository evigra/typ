{
    "name": "Landed Costs for TYP",
    "version": "14.0.0.2.0",
    "author": "Vauxoo",
    "category": "Generic Modules/Account",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "stock_landed_costs",
    ],
    "demo": [
        "demo/journal_demo.xml",
        'demo/purchase_demo.xml',
        "demo/product_demo.xml",
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
