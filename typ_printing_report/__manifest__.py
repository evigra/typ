{
    "name": "TyP Printing Report",
    "version": "14.0.0.1.0",
    "license": "LGPL-3",
    "category": "",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    # any module necessary for this one to work correctly
    "depends": [
        "stock",
        # 'barcodes_generator_product',
        # 'base_report_to_printer',
    ],
    # always loaded
    "data": [
        # "wizard/stock_product_print_label_view.xml",
        "report/report_product_label.xml",
        # "views/stock_picking_view.xml",
        "security/ir.model.access.csv",
    ],
    # only loaded in demonstration mode
    "demo": [],
    "installable": True,
}
