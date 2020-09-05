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
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase_requisition',
        'typ_default_warehouse_from_sale_team',
    ],

    # always loaded
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'data/base_action_rule.xml',
        'reports/layout.xml',
        'reports/purchase_order.xml',
        'reports/purchase_quotation.xml',
        'views/purchase_view.xml',
        'views/partner_view.xml',
        'views/res_company_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
