# -*- coding: utf-8 -*-
{
    'name': "TyP Portal",
    'author': "T&P Refrigeracion",  # pylint: disable=C8101
    'website': "http://www.typrefrigeracion.com",
    'license': 'LGPL-3',
    'category': '',
    'version': '8.0.1.0.0',

    'depends': [
        'portal_sale',
        'l10n_mx_facturae_base'
    ],

    'data': [
        'views/portal_inherit_view.xml',
        'views/account_invoice_view.xml',
        'data/ir_actions_server.xml',
        'data/base_action_rule.xml',
    ],
}
