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
    "name": "stock moves report", 
    "version": "0.1", 
    "author": "cmexia", 
    "category": "TyP", 
    "description": """
This Module allow you to get an stock moves report in stock.
""", 
    "website": "not available", 
    "license": "", 
    "depends": [ 
        "stock",
    ], 
    "demo": [], 
    "data": [
        "report/moves.xml",       
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}
