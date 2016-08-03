# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 HESATEC (<http://www.hesatecnica.com>).
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

from openerp.osv import osv, fields
import time
import dateutil
import dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from openerp import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import openerp
from datetime import date, datetime, time, timedelta
from openerp import SUPERUSER_ID

class comission_config(osv.Model):
    _name = 'comission.config'
    _description = 'Parameters for Comission'

    _columns = {
        'name': fields.char('Description', size=128, required=False),
        'nominal_lines_ids': fields.one2many('nominal.lines.model', 'nominal_ref_id', 'Calculo de Comisiones'),

        'company_nominal_ids': fields.many2many('res.company','comissions_company_rel_calc','config_id','company_id', 'Empresas', help=""" 
            Define la(s) Empresas para las Cuales Aplicara el Calculo de la Comision, por defecto el Sistema siempre tomara la del Vendedor, pero puede Existir Excepciones y es donde ponemos las compañias.
            Un Ejemplo Claro seria el Calculo de una Comision para las Facturas Pagadas de la Compañia 1, Compañia 2 y Compañia 3.""", ),
      
    }
    _defaults = {
    'name': 'Parameters',
    }

comission_config()

class nominal_lines_model(osv.Model):
    _name = 'nominal.lines.model'
    _description = 'Parameters for Comission Percentage Nominal'
    _columns = {
        'name': fields.text('Notas'),
        'detail_comission': fields.char('Concepto de Comision', help='Define el Concepto por la cual se aplicara esta Comision', size=128),
        'python_code': fields.text('Codigo Python'),
        # 'result_python_code': fields.float('Resultado Ejecucion Codigo Python', digits=(14,2)),
        'special_calculate': fields.boolean('Calculo Especial', help="Permite al Administrador del Sistema Ingresar Codigo Python para realizar la aplicacion de Formulas Especiales, formas de Evaluo, etc\n \
    Los parametros que Reciben para el Calculo son las siguientes: \n \
    - cr (Cursor de BD) \n - uid (Id Usuario que Usa el Asistente) \n - ids (Id del Asistente) \n - salesman_id (Id del Vendedor a Evaluar) \n - account_invoice_parent_ids (Listado de Facturas del Periodo que Evaluamos) \n \
    Aqui podemos utilizar todas Funciones ORM, self, create, etc.., cada vez que disparemos esta funcion es necesario crear el Registro del Tipo: \n \
    temporal_results_nominal = self.pool.get('temporal.results.nominal') \n \
    temporal_id = temporal_results_nominal.create(cr, uid, {\n \
                                                    'result_python_code': total_comission, \n \
                                                    'nominal_id': self_br.id,\n \
                                                    'date': datetime.now().strftime('%Y-%m-%d'), \n \
                                                    'name': self_br.detail_comission,}, context=None)", ),

        'margin_percentage_initial': fields.float('Margen Inicial%', digits=(3,2), required=True, help='Definelo en Porcentaje Decimal Ejemplo 30.0%, etc... \n Para el calculo de comisiones por Codigo Python si tomaran en cuenta algun margen minimo, ponerlo en el campo Margen Inicial, ejemplo para aquellos cuyo margen sea mayor a 10 %'),
        'margin_percentage_final': fields.float('Margen Final %', digits=(3,2), required=True, help='Definelo en Porcentaje Decimal Ejemplo 30.0%, etc...\n Si es necesario declarar una linea como final o tope,  en donde el margen Superior es el inicial dejarlo en 0.0, EJemplo ventas con margen mayor a 30 y en margen final no tendra limitante, dejar 0.0'),
        'percentage': fields.float('Porcentaje de Comision %', digits=(3,2), required=True, help='Definelo en Porcentaje Decimal Ejemplo 30.0%, etc...'),
        'final_day': fields.integer('Limite Dias de Pago', required=True, help='Limite de Dias de Pago para Aplicar la Comision, despues de que la Factura fue Vencida', ),
        'nominal_ref_id': fields.many2one('comission.config', 'ID Return', ondelete="cascade"),

        'product_category_ids': fields.many2many('product.category','nominal_category_p_rel','nominal_id','category_id', 'Categorias de Productos', help=""" 
            Define las Categorias de Productos que se tomaran en cuenta para las Comisiones, Tomando en Cuenta Que la categoria Seleccionada puede ser la Categoria Padre o las Catgeorias Hijas""", ),
        'general': fields.boolean('Comision por Defecto', help='Comisiones que se aplican a este Grupo de Vendedores de Forma Extra o de Forma Periodica independientemente de un rango de margenes'),

    }
    _defaults = {
    }

    def _check_percentage(self, cr, uid, ids, context=None):
        if not ids:
            return True
        for r in self.browse(cr, uid, ids, context=context):
            if r.percentage > 100 or r.margin_percentage_initial > 100 or r.margin_percentage_final > 100:
                return False
        return True


    def execute_code(self, cr, uid, ids, salesman_id, account_invoice_parent_ids, date_start, date_end, context=None):
        result = 0.0
        self_br = self.browse(cr, uid, ids[0], context=None)
        if self_br.python_code:
            exec self_br.python_code
        return True

    _constraints = [
        (_check_percentage, 'Error ! The percentage can not be greater than 100 %', ['%'])
    ]

    _order = 'percentage desc'
nominal_lines_model()

class temporal_results_nominal(osv.osv):
    _name = 'temporal.results.nominal'
    _description = 'Resultados de Ejecucion Comisiones Python'
    _columns = {
        'result_python_code': fields.float('Resultado Ejecucion Codigo Python', digits=(14,2)),
        'nominal_id': fields.many2one('nominal.lines.model', 'Parametro Calculo de Comision'),
        'date': fields.date('Fecha Ejecucion'),
        'name': fields.char('Nota', size=128),
    }
    _defaults = {  
        }
    _order = 'id desc' 
# class comission_config_nominal(osv.Model):
#     _name = 'comission.config.nominal'
#     _description = 'Parameters for Comission Percentage Nominal'
#     _columns = {
#         'team_crm_id': fields.many2one('crm.case.section', 'Equipo de Venta', required=True),
#         'name': fields.char('Description', size=128, required=True),
#         'comission_id': fields.many2one('comission.config', 'ID Return'),
#         'nominal_lines_ids': fields.one2many('nominal.lines.model', 'nominal_id', 'Calculo de Comisiones'),
#     }
#     _defaults = {
#     }

# comission_config_nominal()