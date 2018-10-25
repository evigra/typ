# -*- coding: utf-8 -*-
{
    'name': "typ_sale",
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'LGPL-3',
    'category': '',
    'version': '11.0.0.0.1',

    'depends': [
        'sale_margin',
        'typ_stock',
        'crm',
        'payment_term_type',
        'base_automation',
        'product_supplierinfo_for_customer_sale',
    ],

    'data': [
        'data/res_groups.xml',
        'data/base_action_rule.xml',
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
        'views/pricelist_view.xml',
    ],
    'demo': [
        'demo/sale_data_demo.xml',
    ],
}
