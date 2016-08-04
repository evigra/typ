# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.report import report_sxw
import time


class comission_report(report_sxw.rml_parse): # report_sxw es para decirle que va a tomar esa libreria de python
    def __init__(self, cr, uid, name,context=None): # Esta clase no genera nada en base de datos
        super(comission_report, self).__init__(cr, uid, name, context=context) # con super tomamos la clase super ya explicada anteriormente
        self.localcontext.update({ # un diccionario definido como localcontext que update va contener todos los parametros para nuestro reporte
            'time': time,
        })


report_sxw.report_sxw(
    'report.invoice.comission.report.salesman', #report.%s   donde %s es el nombre del reporte en el xml siempre va report mas el nombre de nuestra clase
    'invoice.comission.report', # aqui es el nombre de la clase de nuestra clase session que contendra nuestro reporte
    'argil_typ_comissions/report/comission_report.mako',#addons/path_rml_del_xml la ruta de nuestro rml se encuentra en nuestro sxw
    parser=comission_report,# por ultimo un parse con el nombre de la clase
    header=True # le decimos que nuestra cabecera sea False
)


