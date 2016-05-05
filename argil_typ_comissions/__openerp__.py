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
    'name': 'Calculo de Comisiones de Ventas',
    'version': '1',
    "author" : "HESATEC",
    "category" : "TyP",
    'description': """
       Este modulo adapta una metodologia para aplicar comisiones de ventas sobre el pago de las facturas....
       Para utilizarlo es necesario identificar en la parte de usuarios a cuales se les aplicara estas comisiones

       Equipos de Ventas que comisionan:\n

        - Vendedor de mostrador
        - Ingeniero de Venta
        - Vendedor Empresarial
        - Gerente de Sucursal

        - Gerente de División: equipo de aire acondicionado, equipo de refrigeración, refacciones \n

        Seguridad:\n

        - Existe un Grupo Llamado Gestion de Comisiones, este Grupo permite el Acceso al modulo de Comisiones para otros Usuarios, calculo y consulta de Reportes de Comisiones.
    """,
    "website" : "http://www.hesatecnica.com/",
    "license" : "AGPL-3",
    "depends" : ["account","sale","purchase","account_voucher","account_accountant","crm","report_webkit"],
    "data" : [
                    'calculate_commissions_view.xml',
                    'res_users_view.xml',
                    'invoice_analisis_comissions_view.xml',
                    'account_invoice_view.xml',
                    'wizard/wizard_invoice_analisis_comissions_view.xml',
                    'wizard/wizard_invoice_lines_filters_view.xml',
                    'parameters_update.xml',
                    'report/comission_report.xml',
                    'security/comissions_security.xml',
                    'security/ir.model.access.csv',
                    ],
    "installable" : True,
    "active" : False,
}
