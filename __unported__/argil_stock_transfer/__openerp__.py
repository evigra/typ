# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Argil Consulting (<http://www.argil.mx>)
#    Information:
#    Israel Cruz Argil  - israel.cruz@argil.mx
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
    "name"        : "Stock Transfers adding Landed Costs",
    "version"     : "1.2.1",
    "category"    : "Stock",
    'complexity'  : "normal",
    "author"      : "Argil Consulting",
    "website"     : "http://www.hesatecnica.com",
    "depends"     : ["purchase","argil_multi_warehouse_view", 'stock_account'],
    "summary"     : "Management of Stock Transfers between Subsidiaries",
    "description" : """
Stock Subsidiary Transfer
==========================

This application allows you to manage Stock Transfers between several Warehouses.
You can manage Stock Transfers between:
 - Distribution Center to Subsidiary
 - Subsidiary to Subsidiary
 - Subsidiary to Distribution Center

 Also you can add Expenses related to transfer, like:
 - Freight
 - Other expenses (Packaging, Product Load/Unload, etc).
""",

    "data" : [
        'security/stock_transfer_security.xml',
        'security/ir.model.access.csv',
        'stock_transfer_view.xml',
        'stock_sequence.xml',
        #'stock_transfer_workflow.xml',
        ],
    "application": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
