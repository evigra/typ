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
    'name': 'Actualizacion de Fechas de Recepcion',
    'version': '1',
    "author" : "Argil Consulting",
    "category" : "TyP",
    'description': """

            Este modulo agrega un Asistente para la Actualizacion de los Campos de Fecha de Recepcion.
                --> El Asistente se Encuentra al Seleccionar Registros de Albaranes de Entrada, Pestaña Mas y Seleccionar la Opcion "Actualizacion Fechas/Recepcion"
                --> El Asistente se Encuentra al Seleccionar Registros de Productos a Recibir, Pestaña Mas y Seleccionar la Opcion "Actualizacion Fechas/Recepcion"
            
            Fechas de Embarque:
                --> El modulo Agrega las Fechas de Embarque en las Lineas del Pedido.
                --> El modulo Agrega en la vista de lista, el embarque mas reciente a llegar.
    """,
    "website" : "http://poncesoft.blogspot.com",
    "license" : "AGPL-3",
    "depends" : ["purchase","stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    'update_view.xml',
                    'purchase_view.xml',
                    'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
