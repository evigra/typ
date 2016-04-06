# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
############################################################################
#    Coded by: Israel Cruz Argil (israel.cruz@argil.mx)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Supply Request in Sale Order Line',
    'version': '1.0',
    'category': 'Sale',
    'description': """ 
Supply Request in Sale Order Line
=================================

This module adds new field in Sale Order Line (From Warehouse), so when Procurement Method == Supply Request, 
then user can selects the Warehouse that will be the origin Warehouse the product will be shipped.


""",
    'author': 'Argil Consulting',
    'depends': ['argil_supply_request'],
    'data': ['sale_order_line_view.xml',
            ],
    'website': 'http://www.argil.mx',
    'installable': True,
    'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
