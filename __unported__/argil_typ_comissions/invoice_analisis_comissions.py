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

class invoice_comission_report(osv.osv):
    _name = 'invoice.comission.report'
    _description = 'Invoice Comissions Report by Salesman...'

    def _get_total_units_comission(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr,uid,ids,context=context):
            res[rec.id] = {
                'total_comission_generate': 0.0,
            }
            total_comission = 0.0
            for rec_lines in rec.report_lines:
                total_comission += rec_lines.comission
            if not rec.report_lines:
                res[rec.id]['total_comission_generate'] = 0.0
            else:
                res[rec.id]['total_comission_generate'] = total_comission
        return res


    _columns = {
        'name': fields.char('Report Reference', size=256),
        'date': fields.datetime('Date', required=False),
        'date_start': fields.datetime('Date Start'),
        'date_end': fields.datetime('Date End', required=False),
        'user_id': fields.many2one('res.users', "Salesman"),
        'notes': fields.text('Notes'),
        'report_lines':fields.one2many('invoice.comission.report.line','report_id','Invoice Report Lines'),
        'company_id': fields.related('user_id','company_id',type='many2one',relation='res.company',string='Company', store=False, readonly=True),
        'total_comission_generate': fields.function(_get_total_units_comission, string="Comission Total", method=True, type='float', digits=(15,2), multi='volume', store=True),
        'amount_acumulate_invoice': fields.float('Monto Acumulado de Facturas', digits=(20,4)),
        'log': fields.char('Bitacora', size=256),
    }

    _defaults = {
#        'date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
#        'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'sale.order.report.filter.oil')
        }

    _order = 'id desc' 
    def create(self, cr, uid, vals, context=None):
        sequence = self.pool.get('ir.sequence').get(cr, uid, 'invoice.comission.report')
        if sequence:
            vals['name'] = sequence
        else:
            return True
        return super(invoice_comission_report, self).create(cr, uid, vals, context=context)

    def print_report(self, cr, uid, ids, context=None):
        res = {
            'type': 'ir.actions.report.xml',
            'report_name': 'invoice.comission.report.salesman',
            'datas': {
                        'model' : 'invoice.comission.report',
                        'ids'   : ids,
                        }
                    }
        return res
invoice_comission_report()

class  invoice_comission_report_line(osv.osv):
    _name = 'invoice.comission.report.line'
    _description = 'Invoice Comissions Report Lines'
    _rec_name = 'invoice_id' 
    _columns = {
        # 'name': fields.char('Description', size=256),
        'date_invoice': fields.date('Fecha Factura'),
        'origin': fields.char('Origen', size=128),
        'comission': fields.float("Comission", digits=(14,4)),
        # 'margin_percentage': fields.float("Margen %", digits=(8,2)),
        # 'percentage': fields.float("Percentage", digits=(8,2)),
        'report_id':fields.many2one('invoice.comission.report', 'ID Referencia', ondelete='cascade'),
        'amount_payment': fields.float("Subtotal", digits=(14,4)),
        'payment_days': fields.integer("Paydays"),
        'invoice_id': fields.many2one('account.invoice', 'Factura'),
        'date_payment_real': fields.related('invoice_id','date_payment_real', string="Fecha Liquidacion Factura", type="date"),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        ##### REFERENCE ######
        'invoice_line_detail_ids': fields.one2many('invoice.report.line', 'line_report_id', 'Detalle Facturas'),
    }

    _defaults = {
#        'pedido': True,
        }
invoice_comission_report_line()

class  invoice_report_line(osv.osv):
    _name = 'invoice.report.line'
    _description = 'Detalle Lineas de Facturas'
    _rec_name = 'line_id' 
    _columns = {
        'line_id': fields.many2one('account.invoice.line', 'Linea de Factura'),
        'product_id': fields.many2one('product.product', 'Producto'),
        'subtotal_cost': fields.float("Costo Compra", digits=(14,2)),
        'subtotal_line': fields.float("Subtotal Venta", digits=(14,2)),
        'margin_percentage': fields.float("Margen %", digits=(8,2)),
        'margin_amount': fields.float("Margen", digits=(8,2)),
        'percentage_comission': fields.float("Comision %", digits=(8,2)),
        'amount_comission': fields.float("Comision", digits=(8,2)),
        'notes': fields.text('Notas'),
        ##### REFERENCE #######
        'line_report_id': fields.many2one('invoice.comission.report.line', 'ID Ref'),
    }

    _defaults = {
#        'pedido': True,
        }
invoice_report_line()
