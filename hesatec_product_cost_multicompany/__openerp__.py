# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Hesatec - http://www.hesatecnica.com
#    All Rights Reserved.
#    (openerp@hesatecnica.com)
############################################################################
#    Coded by: Israel Cruz (israel.cruz@hesatecnica.com)
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
    "name" : "hesatec_product_cost_multicompany",
    "version" : "1.0",
    "author" : "Hesatec",
    "category" : "Addons",
    "description" : """This module changes default behavior of Average Cost Computation and Standard Price in Multicompany environment
    """,
    "website" : "http://www.hesatecnica.com/",
    "license" : "AGPL-3",
    "depends" : [
            "stock",
            "sale",
            "purchase",
        ],
    "data" : [
        'security/product_cost_multicompany_security.xml',
        'security/ir.model.access.csv',
        'product_cost_multicompany_view.xml',
    ],
    "installable" : True,
    "active" : False,
}
