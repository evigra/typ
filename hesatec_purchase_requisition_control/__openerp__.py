# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Hesa Tecnica - http://www.hesatecnica.com/
#    All Rights Reserved.
#    info hesatecnica (openerp@hesatecnica.com)
#
#    Coded by: Israel Cruz Argil (israel.cruz@hesatecnica.com)
#
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
#

{
    "name": "Purchase Requisition Management",
    "version": "1.0",
    "author": "Hesatec",
    "category": "Purchase",
    "description" : """
Purchase Requisition Management
===============================

This module can help you to manage Purchse Requisition to ensure that all products in requisition are purchased.


    """,
    "website": "http://www.hesatecnica.com/",
    "license": "AGPL-3",
    "depends": [
            "purchase_requisition",
                ],
    "demo": [
    ],
    "data": [
        'view/purchase_requisition_view.xml',
    ],
    "installable": True,
    "active": False,
}
