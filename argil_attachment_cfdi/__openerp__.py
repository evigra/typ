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
    'name': 'Adjuntar Factura CFDI y Plantillas para Enviarla',
    'version': '1',
    "author" : "Argil Consulting",
    "category" : "TyP",
    'description': """
            Este modulo Añade las Siguientes Caracteristicas a la Facturacion Electronica de Mexico:
                - Un reporte CFDI hecho con la Tecnologia iReport y el modulo de OpenERP Jasper Reports.
                - Un asistente para Adjuntar el reporte Mencionado Anteriormen.
                - Un Asistente para Enviar el Archivo XML y el reporte CFDI de Jasper.
                - Un Asistente para el Envio de la Factura y XMl de la Nomina CFDI.
                - El envio Masivo de PDFS y XMLS para un Solo Cliente, seleccionando Varios Registros de Facturas.

    """,
    "website" : "http://www.argil.mx/",
    "license" : "AGPL-3",
    "depends" : ["account","l10n_mx_facturae","l10n_mx_ir_attachment_facturae","hr_payroll","l10n_mx_facturae_report"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "account_invoice_view.xml",
                    "massive_view.xml",
                    "mail_compose_message_view.xml",
                    "email_template_jaspe.xml",
                    # "security/ir.model.access.csv",

                    ],
    "installable" : True,
    "active" : False,
}
