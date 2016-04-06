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
    'name': 'Sale Order Shipping Address to Purchase Order',
    'version': '1.0',
    'category': 'Sale',
    'description': """ 
Sale Order Shipping Address to Purchase Order Shipping Address
==============================================================

This module takes Shipping Address in Sale Order, and write it to Customer Address field in Purchase Order.

Procurement Method of Sale Order Line must be On Demand

""",
    'author': 'Argil Consulting',
    'depends': ['sale','purchase'],
    'data': ['sale_order_line_view.xml',
            ],
    'website': 'http://www.argil.mx',
    'installable': True,
    'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
