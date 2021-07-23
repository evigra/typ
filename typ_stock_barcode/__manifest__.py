{
    "name": "Typ Warehouse Management Barcode Scanning",
    "category": "Warehouse",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "version": "14.0.1.0.1",
    "depends": ["stock_barcode", "typ_stock"],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/stock_barcode_templates.xml",
        "views/stock_picking_views.xml",
        "wizard/stock_barcode_product_view.xml",
    ],
    "installable": True,
}
