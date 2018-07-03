# -*- coding: utf-8 -*-
{
    'name': "typ_default_warehouse_from_sale_team",
    'author': "Vauxoo",
    'website': "http://www.vauxoo.com",
    'license': 'LGPL-3',
    'category': '',
    'version': '11.0.0.0.1',

    'depends': [
        'typ_landed_costs',
        'default_warehouse_from_sale_team',
    ],

    'data': [
        'views/sales_team_view.xml',
    ],
    'demo': [
    ],
    'installable': True
}
