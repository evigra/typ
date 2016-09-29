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
    ],
    # always loaded
    'data': [
        'security/res_groups.xml',
        'data/ir_actions_server.xml',
        'data/base_action_rule.xml',
        'views/procurement_rule_view.xml',
        'views/stock_view.xml',
        'views/stock_picking_view.xml',
        'security/res_groups.xml',
        'wizard/view_procurement_compute_wizard_inh.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/stock_data.xml',
    ],
    'installable': True,
}
