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
    "name" : "Account Invoice Workflow Test Paid",
    "version" : "1.0",
    "category" : "Account",
    'complexity': "Easy",
    "author" : "Argil Consulting",
    "website": "http://www.argil.mx",
    "depends" : ["account"],
    "description": """
Account Invoice Workflow Test Paid
==================================

This module adds validation if Account Invoice balance is zero, then record changes to Paid State
""",
    "demo_xml" : [],
    "init_xml" : [],
    "update_xml" : [],
    "active": False,
    'application': False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

