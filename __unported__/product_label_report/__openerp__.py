#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP
#    All Rights Reserved
###############Credits######################################################
#    Coded by: cmexia carlos.lia.hmo@gmail.com
#    Planified by: 
#    Audited by:
#    Customized by:
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################
{
    "name": "Product Label Report", 
    "version": "0.1", 
    "author": "cmexia", 
    "category": "Generic Modules/Others", 
    "description": """
This module will generate a:
Product Label report in pdf format with sizes compatible with termic printers
        NOTE: You may configure your printer paper size to:
                - w: 100.00mm h:60.00mm (Large)
                - w: 63.00mm h:25.00mm (Medium)
                - w: 37.00mm h:25.00mm  (Small)
Works with multiple selection of rows.
If you want your custom sticker, you can base your code with this one.

""", 
    "website": "not available", 
    "license": "", 
    "depends": [
        "product", 
    ], 
    "demo": [], 
    "data": [
        "report/label.xml",       
    ], 
    "update_xml": [
        "product_view.xml"
    ],
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}
