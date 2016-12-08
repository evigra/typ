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
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'partner_credit_limit',
        'account_voucher_tax',
        'typ_sale',
    ],
    # always loaded
    'data': [
        'data/account_data.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/account_voucher_tax_view.xml',
        'views/account_bank_statement_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
}
