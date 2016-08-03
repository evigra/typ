# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://www.argil.mx/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)
############################################################################
#    Coded by: german_442 email: (german.ponce@argil.mx)
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
    'name': 'Eliminar Poliza Contable al Cancelar Factura',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "Sales",
    'description': """
    
    FACTURACION:

        --> Elimina la Poliza al Cancelar la Factura Validada.
    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    # "sale_view.xml",
                    # "purchase_view.xml",
                    # "invoice_view.xml",
                    #'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
