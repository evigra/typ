# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 german_442
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@argil.mx)
############################################################################
#    Coded by: german_442 email: (cherman.seingalt@gmail.com)
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
    'name': 'Revision de Existencias por Producto',
    'version': '1',
    "author" : "Argil Consulting",
    "category" : "TyP",
    'description': """

            Este modulo agrega un Asistente que Muestra las Existencias del Producto Seleccionado.
                --> El Asistente se encuentra en Ventas/Productos/ Consultar Existencias
    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    "depends" : ["purchase"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    #'customs_view.xml',
                    'stocks_view.xml',
                    'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
