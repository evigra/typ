{
    "name": "Typ Stock",
    "version": "14.0.0.0.1",
    "license": "LGPL-3",
    "category": "",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    # any module necessary for this one to work correctly
    "depends": [
        "sale_stock",
        # 'stock_no_negative',
        # 'stock_picking_show_return',
    ],
    # always loaded
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/stock_sequence.xml",
        # "views/stock_view.xml",  -> TODO: review on v14.0
        # "views/stock_picking_view.xml",   -> TODO: review on v14.0
        # "views/product_view.xml",   -> TODO: review on v14.0
        # "views/stock_manual_transfer_view.xml",   -> TODO: review on v14.0
        "views/view_procurement_compute_wizard_inh.xml",
        "report/report_stock_views.xml",
        "report/report_stockpicking.xml",
        "report/report_stockpicking_wobc.xml",
        "report/stock_report_deliveryslip.xml",
        # "views/stock_account_view.xml",   -> TODO: review on v14.0
        # "views/stock_inventory_view.xml",   -> TODO: review on v14.0
    ],
    # only loaded in demonstration mode
    "demo": [
        # "demo/stock_data.xml", # -> TODO: review on v14.0
    ],
    "installable": True,
}
