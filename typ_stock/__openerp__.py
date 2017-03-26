# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Yennifer Santiago <yennifer@vauxoo.com>
#    planned by: Julio Serna <julio@vauxoo.com>
############################################################################
{
    'name': "Typ Stock",
    'version': '8.0.0.1.0',
    'license': 'LGPL-3',
    'category': '',
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    # any module necessary for this one to work correctly
    'depends': [
        'delivery',
        'typ_purchase',
        'product_unique_serial',
    ],
    # always loaded
    'data': [
        'data/ir_actions_server.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/base_action_rule.xml',
        'data/ir_cron.xml',
        'views/procurement_rule_view.xml',
        'views/stock_view.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_picking_view.xml',
        'views/product_view.xml',
        'views/stock_quant_view.xml',
        'wizard/view_procurement_compute_wizard_inh.xml',
        'wizard/stock_serial_view.xml',
        'wizard/pedimento_product_wizard.xml',
        'wizard/stock_transfer_details.xml',
        'report/report_stockpicking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/stock_data.xml',
        'demo/stock_data_reordering_rule.xml',
    ],
    'installable': True,
}
