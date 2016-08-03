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
    'name': 'Ventas de Mostrador',
    'version': '1',
    "author" : "Argil Consulting",
    "category" : "TyP",
    'description': """
    
    VENTAS DE MOTRADOR:
    
    Modulo Extra para Generar Pedidos de Venta, con restricciones Especificas

    Este Modulo va ligado al Limite de Credito, si una Venta no es de Contado, entonces, tenemos que especificar el Plazo de Pago.
    """,
    "website" : "http://www.argil.mx",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","sale_credit_client","l10n_mx_sale_payment_method"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "sale_view.xml",
                    #'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
