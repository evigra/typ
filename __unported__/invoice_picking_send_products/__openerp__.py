# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://www.hesatecnica.com.com/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@hesatecnica.com)
############################################################################
#    Coded by: german_442 email: (german.ponce@hesatecnica.com)
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
    'name': 'Productos Enviados en Pedidos de Compra',
    'version': '1',
    "author" : "German Ponce Dominguez",
    "category" : "TyP",
    'description': """

        Este modulo Agrega Lineas, para conocer que Productos y Cantidad de han Enviado desde Albaranes de Salida, que tengan relacion con una Compra.
        
        Modificaciones:

            - Agrega el Margen de Productos que se han recibido en Porcentaje.
            - Agrega el Margen de Productos recbidos en Monto.
    """,
    "website" : "http://poncesoft.blogspot.com",
    "license" : "AGPL-3",
    "depends" : ["purchase","sale","stock","pedimentos_customs"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    'account_view.xml',
                    # 'stocks_view.xml',
                    'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
