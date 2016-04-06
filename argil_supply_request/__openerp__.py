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
    'name': 'Supply request to main company',
    'version': '1.7.2',
    'author': 'Argil',
    'category': 'Stock Management',
    'images': [],
    'website': '',
    'description': """
This module adds supply request feature.
========================================
*It adds new procure method 'Make to Supply Request' and in product reordering rule has field supply_internally 
and can specify source warehouse to where we can send the request.

Creates supply request
* When In a sale order procure method is 'On supply request' and  
* When running Scheduler (Procurement) if product reordering rule has field supply_internally 
active, instead of creating Purchase Order or Purchase Requisition then create new record in 
stock.supply_request in Draft State


""",
    'depends' : ['sale_stock',"argil_multi_warehouse_view"],
    'demo': [],
    'data': [
             'security/ir.model.access.csv',
             'wizard/attend_supply_request_view.xml',
             'stock_view.xml',
             'supply_request_view.xml',
             'supply_request_workflow.xml',
    ],
    'auto_install': False,
    'test': [
        
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
