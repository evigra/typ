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
    'name': 'Ejecucion de Querys y Parches',
    'version': '1',
    "author" : "Argil Consulting/German Ponce Dominguez",
    "category" : "TyP",
    'description': """

            Este modulo agrega un Asistente que permite Ejecutar el Codigo, con una llave maestra.

    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    "depends" : [],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    #'customs_view.xml',
                    'patch.xml',
                    # 'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
