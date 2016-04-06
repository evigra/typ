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
import tempfile
from xml.dom import minidom
import os
import base64
import hashlib
import tempfile
import os
import codecs
from openerp import SUPERUSER_ID


class purchase_order(osv.osv):
    _inherit ='purchase.order'
    _name = 'purchase.order' 

    def _get_date_shipment(self, cr, uid, ids, field_name, arg, context=None):
        result={}
        for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            p_date = []
            for line in rec.order_line:
                if line.shipment_t_date:
                    p_date.append(str(line.shipment_t_date))
            
            if p_date:
                p_date.sort()
                result[rec.id] = p_date[0]
        return result
    _columns = {
    'shipment_t_date': fields.date("Fecha de Embarque"),
    'proximite_date_shipment': fields.function(_get_date_shipment, method=True, type="date", string="Fecha de Embarque", help='Fecha de Embarque mas Proxima a llegar del Pedido de Compra',  store=True),

    }

    def on_change_shipment(self, cr, uid, ids, order_line, shipment_t_date,context=None):
        res = {}
        line_obj = self.pool.get('purchase.order.line')
        for line in order_line:
            product_obj = self.pool.get('product.product')
            required_date = False
            if line[1] != False:
                line_br = line_obj.browse(cr, uid, line[1], context=None)
                if line_br.product_id:
                    if line_br.product_id.type != 'service':
                        required_date = True
                        line_obj.write(cr, uid, [line[1]], {'shipment_t_date':shipment_t_date,"required_date_product":required_date},context=None)
            else:
                if 'product_id' in line[2]:
                    produc_br = product_obj.browse(cr, uid, line[2]['product_id'], context=None)
                    if produc_br.type != 'service':
                        required_date = True
                        line[2].update({'shipment_t_date':shipment_t_date,"required_date_product":required_date})

        res['order_line'] = [x for x in order_line]
        return {'value':res}
purchase_order()

class purchase_order_line(osv.osv):
    _inherit ='purchase.order.line'
    _name = 'purchase.order.line' 
    _columns = {
    'required_date_product': fields.boolean('Fecha de Embarque Requerida'),
    'shipment_t_date': fields.date("Fecha de Embarque"),
    }
    # def on_change_shipment(self, cr, uid, product_id, shipment_t_date, ids,context=None):
    #     res = {}
    #     res['shipment_t_date'] = shipment_t_date
    #     if product_id == []:
    #         print "### lista"
    #         product_id = product_id[0]
    #     print "#### product id", product_id
    #     product_obj = self.pool.get('product.product')
    #     pr_br = product_obj.browse(cr, uid, product_id, context=None)
    #     print "######### PRODUCT ID", product_id
    #     print "######### PRODUCT ID", pr_br.name
    #     return {'value':res}

purchase_order_line()

class update_shipment_purchase_line(osv.osv_memory):
    _name = 'update.shipment.purchase.line'
    _description = 'Actualizar Fecha de Recepcion'
    _columns = {
    'datetime_act': fields.date('Fecha/Hora Recepcion', required=True),
    }
    def _get_date(self, cr, uid, context=None):
        date_act = False
        active_ids = context and context.get('active_ids', False)
        if active_ids:
            order_line = self.pool.get('purchase.order.line')
            line_br = order_line.browse(cr, uid, active_ids, context=None)
            if line_br[0].date_planned:
                date_act = line_br[0].date_planned
        return date_act
    _defaults = {  
    'datetime_act': _get_date,
        }
    def write_date(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', False)
        order_line = self.pool.get('purchase.order.line')
        line_br = order_line.browse(cr, uid, active_ids, context=None)
        order_obj = self.pool.get('purchase.order')
        #attrs="{'invisible':[('parent.state','not in',('sent','confirmed','approved'))]}"
        for rec in self.browse(cr, uid, ids, context=None):
            if line_br[0].order_id.state not in ('draft','sent','confirmed','approved','except_picking','except_invoice'):
                raise osv.except_osv(_('Error '), 
                    _('El Pedido se encuentra en Estado Finalizado o Cancelado'))
            line_br[0].order_id.write({})
            line_br[0].order_id.write({})
            order_line.write(cr, uid, active_ids, {'date_planned':rec.datetime_act})
            order_obj.message_post(cr, uid, [line_br[0].order_id.id], body=_("Fecha de Recepcion Actualizara <b> %s </b> para el Producto <b>%s</b>.") % (rec.datetime_act,line_br[0].product_id.name),  context=context)
        return True

class update_shipment_purchase(osv.osv_memory):
    _name = 'update.shipment.purchase'
    _description = 'Actulaizar Fecha de Embarque'
    _columns = {
    'datetime_act': fields.date('Fecha/Hora Embarque', required=True),
    }
    def _get_date(self, cr, uid, context=None):
        date_act = False
        active_ids = context and context.get('active_ids', False)
        if active_ids:
            order_line = self.pool.get('purchase.order.line')
            line_br = order_line.browse(cr, uid, active_ids, context=None)
            if line_br[0].shipment_t_date:
                date_act = line_br[0].shipment_t_date
        return date_act
    _defaults = {  
    'datetime_act': _get_date,
        }
    def write_date(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', False)
        order_line = self.pool.get('purchase.order.line')
        line_br = order_line.browse(cr, uid, active_ids, context=None)
        order_obj = self.pool.get('purchase.order')
        #attrs="{'invisible':[('parent.state','not in',('sent','confirmed','approved'))]}"
        for rec in self.browse(cr, uid, ids, context=None):
            if line_br[0].order_id.state not in ('draft','sent','confirmed','approved','except_picking','except_invoice'):
                raise osv.except_osv(_('Error '), 
                    _('El Pedido se encuentra en Estado Finalizado o Cancelado'))
            line_br[0].order_id.write({})
            line_br[0].order_id.write({})
            order_line.write(cr, uid, active_ids, {'shipment_t_date':rec.datetime_act})
            order_obj.message_post(cr, uid, [line_br[0].order_id.id], body=_("Fecha de Embarque Actualizada <b> %s </b> para el Producto <b>%s</b>.") % (rec.datetime_act,line_br[0].product_id.name),  context=context)
        return True

# class stock_partial_picking(osv.osv):
#     _name = 'stock.partial.picking'
#     _inherit ='stock.partial.picking'
#     _columns = {
#     'pedimento_id': fields.many2one('pedimento.custom', 'Pedimento Aduanal'),
#         }

#     _default = {
#         }

#     def on_change_pedimento(self, cr, uid, ids, pedimento_id, move_ids, picking_id, context=None):
#         res = {}
#         move_ids = move_ids
#         pedimento_obj = self.pool.get('pedimento.custom')
#         pedimento_br = pedimento_obj.browse(cr, uid, pedimento_id, context=None)
#         no_serie = pedimento_br.pedimento_sequence
#         stock_lot_obj = self.pool.get('stock.production.lot')
#         stock_obj = self.pool.get('stock.picking.in')
#         product_ids = []
#         ## Se compone de id_product:id_lote  ejemplo producto coco id = 1 lote del producto 12 quedaria {1:12}
#         product_serie = {}

#         for stock in stock_obj.browse(cr, uid, [picking_id], context=None):
#             for line in stock.move_lines:
#                 product_ids.append(line.product_id.id)
#         product_ids = set(product_ids)
#         for pr in product_ids:
#             vals = {'name':no_serie,'product_id':pr}
#             stock_lot_id = stock_lot_obj.create(cr, uid, vals, context=None)
#             product_serie.update({pr:stock_lot_id})
#         for line in move_ids:
#             if len(line) >= 3:

#                 if type(line[2]) == type({}):
#                     if line[2]['prodlot_id'] == False:
#                         product_id_l = line[2]['product_id']
#                         lote = product_serie[product_id_l]
#                         line[2].update({'prodlot_id':lote})
#         res.update({'move_ids':move_ids})
#         return {'value':res}
# stock_partial_picking()