# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
import calendar
from openerp import SUPERUSER_ID

# Agregamos manejar una secuencia por cada tienda para controlar viajes 
class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"

    def _get_receive(self, cr, uid, ids, field_name, arg, context=None):
        result={}
        margin = 0.0
        for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            qty_product_lines = 0.0
            for line in rec.order_line:
                qty_product_lines += line.product_qty
            qty_received = 0.0
            for line_r in rec.products_received_line:
                qty_received += line_r.product_qty
            if qty_product_lines > 0.0 and qty_received > 0.0:
                margin = (float(qty_received)/float(qty_product_lines))*100
            result[rec.id] = margin
        return result

    def _get_receive_amount(self, cr, uid, ids, field_name, arg, context=None):
        result={}
        margin = 0.0
        for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            amount_total = 0.0
            for line_r in rec.products_received_line:
                amount_total += line_r.amount_total
            result[rec.id] = amount_total
        return result
    _columns = {
        'products_received_line': fields.one2many('picking.invoice.received', 'order_id','Productos Recibidos', readonly=True),
        'margin_products_receive': fields.function(_get_receive, method=True, type="float", digits=(3,2), string="Porcentaje Recepcion %", store=True),
        'margin_amount_receive': fields.function(_get_receive_amount, method=True, type="float", digits=(14,2), string="Monto Recepcion", store=True),
    }
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
                        'products_received_line': False,
                        })
        return super(purchase_order, self).copy(cr, uid, id, default, context=context)

purchase_order()

class picking_invoice_received(osv.osv):
    _name = 'picking.invoice.received'
    _description = 'Lineas de Producto Recibido desde Almacen'
    _rec_name = 'product_id' 
    _columns = {
        'order_id': fields.many2one('purchase.order', 'ID Ref'), 
        'product_id': fields.many2one('product.product', 'Producto'), 
        'product_qty': fields.float('Cantidad Recibido', digits=(14,2)),
        'prodlot_id': fields.many2one('stock.production.lot', 'Numero de Serie'),
        # 'pedimento_id': fields.many2one('stock.production.lot.pedimento', 'Pedimento'),
        'picking_id': fields.many2one('stock.picking', 'Albaran'),
        'amount_total': fields.float('Monto de la Recepcion', digits=(14,4)),
    }

picking_invoice_received()

