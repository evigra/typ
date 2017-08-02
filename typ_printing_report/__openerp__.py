# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Antonio Rogel <arogel@typrefrigeracion.com>
#    planned by: Julio Serna <julio@vauxoo.com>
############################################################################
{
    'name': "TyP Printing Report",
    'version': '8.0.0.1.0',
    'license': 'LGPL-3',
    'category': '',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    # any module necessary for this one to work correctly
    'depends': [
        'stock',
        'product_barcode_generator',
        'base_report_to_printer',
    ],
    # always loaded
    'data': [
        'wizard/stock_product_print_label_view.xml',
        'report/report_product_label.xml',
        'views/stock_picking_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
