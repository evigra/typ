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
    'name': "Typ Account",
    'license': "LGPL-3",
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'category': '',
    'version': '8.0.0.1.1',

    # any module necessary for this one to work correctly
    'depends': [
        'partner_credit_limit',
        'account_voucher_tax',
        'typ_sale',
        'typ_default_warehouse_from_sale_team',
    ],
    # always loaded
    'data': [
        'data/account_data.xml',
        'data/ir_actions_server.xml',
        'data/account_invoice_workflow.xml',
        'views/sale_order_view.xml',
        'views/account_move_line.xml',
        'views/account_invoice_view.xml',
        'views/account_voucher_tax_view.xml',
        'views/account_bank_statement_view.xml',
        'reports/account_invoice_report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
