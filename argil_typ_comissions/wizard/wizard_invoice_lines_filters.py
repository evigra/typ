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


class invoice_line_search_wizard(osv.osv_memory):
    _name = 'invoice.line.search.wizard'
    _description = 'Buscador Avanzado de Lineas de Factura'
    _columns = {
        'date': fields.datetime('Date', required=True),
        'user_id': fields.many2one('res.users','Vendedor', required=True),
        'category_product': fields.one2many('lineas.facturas.categorias.productos', 'busqueda_id','Categorias de Productos'),
        'date_start': fields.date('Fecha Inicial Pago', required=True),
        'date_end': fields.date('Fecha Final Pago', required=True),
        # 'domain': fields.text('Dominio de Busqueda', help='Este campo permite agregar un dominio para Filtrar la informacion Ej. invoice_id.state == paid', )
    }

    def _get_date_start(self, cr, uid, context=None):
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
        year = date_strp.year
        month = date_strp.month
        day = date_strp.day

        date_revision = date_strp - timedelta(days=15)
        return str(date_revision)

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_end': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_start': _get_date_start,
        }

    def search_invoice_line(self, cr, uid, ids, context=None):
        invoice_line_ids = []
        invoice_line_obj = self.pool.get('account.invoice.line')
        product_category = self.pool.get('product.category')
        for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            if rec.category_product:
                category_ids = [x.category_id.id for x in rec.category_product]
                category_parent_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                    ('parent_id','in',tuple(category_ids))
                                                                        ])
                if category_parent_ids:
                    category_parent_2_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                    ('parent_id','in',tuple(category_parent_ids))
                                                                        ])
                    category_ids = category_ids + category_parent_ids + category_parent_2_ids

                invoice_line_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                    ('invoice_id.user_id','=',rec.user_id.id),
                                                                    ('invoice_id.user_reasigned_id','=',False),
                                                                    ('invoice_id.date_payment_real','>=',rec.date_start),
                                                                    ('invoice_id.date_payment_real','<=',rec.date_end),
                                                                    ('invoice_id.state','=','paid'),
                                                                    ('invoice_id.type','=','out_invoice'),
                                                                    ('product_id.categ_id','in',tuple(category_ids))
                                                                    ])
                invoice_reasigned_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                    ('invoice_id.user_reasigned_id','=',rec.user_id.id),
                                                                    ('invoice_id.date_payment_real','>=',rec.date_start),
                                                                    ('invoice_id.date_payment_real','<=',rec.date_end),
                                                                    ('invoice_id.state','=','paid'),
                                                                    ('invoice_id.type','=','out_invoice'),
                                                                    ('product_id.categ_id','in',tuple(category_ids))
                                                                    ])
                if invoice_reasigned_ids:
                    invoice_line_ids = invoice_line_ids + invoice_reasigned_ids
            else:
                invoice_line_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                    ('invoice_id.user_id','=',rec.user_id.id),
                                                                    ('invoice_id.user_reasigned_id','=',False),
                                                                    ('invoice_id.date_payment_real','>=',rec.date_start),
                                                                    ('invoice_id.date_payment_real','<=',rec.date_end),
                                                                    ('invoice_id.type','=','out_invoice'),
                                                                    ('invoice_id.state','=','paid'),
                                                                    ])
                invoice_reasigned_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                    ('invoice_id.user_reasigned_id','=',rec.user_id.id),
                                                                    ('invoice_id.date_payment_real','>=',rec.date_start),
                                                                    ('invoice_id.date_payment_real','<=',rec.date_end),
                                                                    ('invoice_id.type','=','out_invoice'),
                                                                    ('invoice_id.state','=','paid'),
                                                                    ])
                if invoice_reasigned_ids:
                    invoice_line_ids = invoice_line_ids + invoice_reasigned_ids
        return {
                'domain': "[('id','in', ["+','.join(map(str,invoice_line_ids))+"])]",
                'name': _('Lineas de Factura'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice.line',
                'view_id': False,
                'type': 'ir.actions.act_window'
                }

invoice_line_search_wizard()

class lineas_facturas_categorias_productos(osv.osv_memory):
    _name = 'lineas.facturas.categorias.productos'
    _description = 'Categorias Productos'
    _rec_name = 'category_id' 
    _columns = {
    'category_id':fields.many2one('product.category', 'Categoria Producto', required=True),
    'busqueda_id': fields.many2one('invoice.line.search.wizard', 'ID Ref'),
    }
