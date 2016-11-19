# -*- coding: utf-8 -*-
{
    'name': "typ_sale",
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'LGPL-3',
    'category': '',
    'version': '8.0.1.0.0',

    'depends': [
        'sale_margin',
        'sale_stock',
        'typ_stock',
        'default_warehouse_from_sale_team',
    ],

    'data': [
        'data/res_groups.xml',
        'data/ir_actions_server.xml',
        'data/base_action_rule.xml',
        'reports/sale_order.xml',
        'reports/layout.xml',
        'security/ir.model.access.csv',
        'views/sale_order_line_view.xml',
        'views/res_partner_warehouse_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/res_company_view.xml',
        'views/res_config_view.xml',
    ],
    'demo': [
        'demo/sale_data_demo.xml',
    ],
}
