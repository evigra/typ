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
        'base_automation',
        # 'typ_stock',
        'crm',
        'payment_term_type',
    ],

    'data': [
        'data/res_groups.xml',
        'data/base_action_rule.xml',
        # 'reports/sale_order.xml',
        # 'reports/layout.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/sale_order_line_view.xml',
        'views/res_partner_warehouse_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        # 'views/res_company_view.xml',
        'views/res_config_view.xml',
        'views/res_partner_classification_view.xml',
        'views/crm_lead_view.xml',
        'views/sales_team_view.xml',
    ],
    'demo': [
        'demo/sale_data_demo.xml',
    ],
}
