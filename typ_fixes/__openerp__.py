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
    'name': 'Addons Fixes',
    'version': '1',
    "author" : "Argil Consulting - German Ponce Dominguez",
    "category" : "TyP",
    'description': """

            Este modulo soluciona pequeños Bugs como:
            - Eliminacion de la Restriccion de Fechas en Facturas para Proveedores.
            - Agrega el Codigo del Proveedor al Crear Cotizacion desde Solicitud.7
            - Agrega un boton eliminar Poliza, al pusarlo elimina la Poliza y cancela la Factura. Para utilizarlo se bede estar en el Grupo de Facturacion.
            - Corrige el error 200 de Timbrado.
    """,
    "website" : "http://poncesoft.blogspot.com",
    "license" : "AGPL-3",
    "depends" : ["account","account_voucher","l10n_mx_invoice_datetime","purchase_requisition","l10n_mx_facturae_pac_sf","purchase","stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "stock_view.xml",
                    "account_view.xml",
                    ],
    "installable" : True,
    "active" : False,
}
