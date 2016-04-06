# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Argil Consulting - http://www.argil.mx
#    All Rights Reserved.
#    (info@argil.mx)
############################################################################
#    Coded by: Israel Cruz (israel.cruz@argil.mx)
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
    "name" : "Warehouse Stock Real and Virtual Multicompany Independent",
    "version" : "1.0",
    "author" : "Argil Consulting",
    "category" : "Addons",
    "description" : """
Stock Real and Virtual Multicompany Independent
===============================================

This module allows to have stock real and virtual sepparated by company, even
if a company has childs and user has access from parent company, stock real will not sum stock real from child companies
    
    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    "depends" : ["stock",],
    "data" : [],
    "installable" : True,
    "active" : True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: