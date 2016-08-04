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
    'name': 'Purchase Forwarding Agent History',
    'version': '1.1',
    'author': 'Argil',
    'category': 'Purchase Management',
    'images': [],
    'website': '',
    'description': """
This module adds forwarding agent history to purchase.
======================================================


""",
    'depends' : ['purchase'],
    'demo': [],
    'data': [
             'security/ir.model.access.csv',
             'partner_view.xml',
             'purchase_view.xml'
    ],
    'auto_install': False,
    'test': [
        
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
