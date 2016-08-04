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
    'name': 'Satisfying Supply Request with stock transfer',
    'version': '1.4',
    'author': 'Argil',
    'category': 'Stock Management',
    'images': [],
    'website': '',
    'description': """
This module connects supply request with stock transfer.
========================================================

""",
    'depends' : ['argil_supply_request','argil_stock_transfer' ],
    'demo': [],
    'data': [
        #'wizard/load_supply_request_view.xml',
        'wizard/attend_supply_request_view.xml',
        'supply_request_workflow.xml',
        'supply_request_view.xml',
        'stock_transfer_view.xml' 
    ],
    'auto_install': False,
    'test': [
        
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
