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
    'name': 'Fix DIOT move lines',
    'version': '1.0',
    'category': 'Generic Modules/Account',
    'description': """ 
Fix DIOT Move Lines
===================

Este modulo intenta corregir el monto del debe/haber de la reclasificacion de IVA, donde el monto base no cuadra versus el monto del cargo/abono de la reclasificacion de IVA

""",
    'author': 'Argil Consulting',
    'depends': ['l10n_mx_diot_report'],
    'data': ['account_diot_fix_wiz.xml'
            ],
    'website': 'http://www.argil.mx',
    'installable': True,
    'active': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
