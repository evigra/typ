# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Deivis Laya <deivis@vauxoo.com>
#    planned by: Julio Serna <julio@vauxoo.com>
############################################################################
{
    'name': "Typ Purchase",
    'license': "LGPL-3",
    'author': 'Vauxoo',
    'website': 'http://www.vauxoo.com/',
    'category': 'Purchase',
    'version': '8.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase_requisition',
        'typ_partner',
    ],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'reports/layout.xml',
        'reports/purchase_order.xml',
        'reports/purchase_quotation.xml',
        'views/purchase_view.xml',
        'views/partner_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
