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
    'name': 'Stock Warehouse View in multicompany',
    'version': '1.1',
    'author': 'Argil',
    'category': 'Stock Management',
    'images': [],
    'website': '',
    'description': """
This module creates a same copy of stock warehouse to new model stock.warehouse_view. 
So that we will be able to see warehouses of different company. This is a base module needed
for supply request and stock transfer modules


""",
    'depends' : ['stock' ],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
    ],
    'auto_install': True,
    'test': [
        
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
