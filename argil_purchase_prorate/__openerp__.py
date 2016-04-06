# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Landing cost distribution',
    'version': '1.8.1',
    'author': 'Argil',
    'category': 'Purchase Management',
    'images': [],
    'website': '',
    'description': """
This module adds landing cost distribution feature.
===================================================


""",
    'depends' : ['purchase'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        #'wizard/stock_prorate_view.xml',
        'res_config_view.xml',
        'wizard/load_purchase_view.xml',
        'sequence_data.xml',
        'stock_prorate_view.xml',
    ],
    'auto_install': False,
    'test': [
        
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
