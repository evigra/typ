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


### Herencia de Stock Production Lot  #####
# class stock_production_lot(osv.osv):
#     _name = 'stock.production.lot'
#     _inherit = 'stock.production.lot'
#     def _get_stock(self, cr, uid, ids, field_name, arg, context=None):
#         res = super(stock_production_lot, self)._get_stock(cr, uid, ids, field_name, arg, context=context)
#         return res
#     def _stock_search(self, cr, uid, obj, name, args, context=None):
#         res = super(stock_production_lot, self)._stock_search(cr, uid, obj, name, args, context=context)
#         return res
#     _columns = {
#         'stock_available': fields.function(_get_stock, fnct_search=_stock_search, type="float", string="Available", select=True,
#             help="Current quantity of products with this Serial Number available in company warehouses",
#             digits_compute=dp.get_precision('Product Unit of Measure'), store=True),
#         # 'qty_used': fields.integer('Cantidad Utilizada de Lotes'),
#         }

#     _default = {
#         # 'qty_used': 0.0,
#         }
# stock_production_lot()
## Herencia para Modificar un  metodo para Asignacion de Lotes ####

class stock_move_split_lines(osv.osv_memory):
    _name = "stock.move.split.lines"
    _inherit = 'stock.move.split.lines' 
    _columns = {
    'pedimento_id': fields.many2one('stock.production.lot.pedimento','No. Pedimento')

     }
stock_move_split_lines()

class split_in_production_lot(osv.osv_memory):
    _name = "stock.move.split"
    _inherit = 'stock.move.split' 
    _description = "Split in Serial Numbers"
    _columns = {
     }

    def split_especial(self, cr, uid, ids, move_ids, context=None):

        """ To split stock moves into serial numbers

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        use_exist = True
        inventory_id = context and context.get('active_model', False)
        prodlot_obj = self.pool.get('stock.production.lot.pedimento')
        inventory_obj = self.pool.get('stock.inventory')
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                if use_exist:
                    lines = [l for l in data.line_exist_ids if l]
                else:
                    lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Error Procesamiento!'), _('La Cantidad de Pedimentos/Series %d de %s supera la Cantidad Disponible (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        self.pool.get('stock.move').log(cr, uid, move.id, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                        'product_uos_qty': uos_qty,
                        'state': move.state
                    }
                    if quantity_rest > 0:
                        current_move = move_obj.copy(cr, uid, move.id, default_val, context=context)
                        if inventory_id and current_move:
                            inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = move.id
                    prodlot_id = False
                    if use_exist:
                        prodlot_id = line.pedimento_id.id
                    if not prodlot_id:
                        prodlot_id = prodlot_obj.create(cr, uid, {
                            'name': line.name,
                            'product_id': move.product_id.id},
                        context=context)

                    move_obj.write(cr, uid, [current_move], {'pedimento_id': prodlot_id, 'state':move.state})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        update_val['product_uos_qty'] = uos_qty_rest
                        update_val['state'] = move.state
                        move_obj.write(cr, uid, [move.id], update_val)

        return new_move

    def split_lot(self, cr, uid, ids, context=None):
        res = super(split_in_production_lot, self).split_lot(cr, uid, ids, context)

        stockable_line_pool = self.pool.get("stock.prorate.stock.line")
        active_ids = context.get('active_ids', False)
        active_model = context and context.get('active_model', False)
        stock_obj = self.pool.get('stock.move')
        stock_prorate = self.pool.get('stock.prorate')
        prorate_id = []
        for stock in stock_obj.browse(cr, uid, active_ids, context=None):
            stock_ids = stock_obj.search(cr, uid, [('prorate_id','=',stock.prorate_id.id),
                                                    ('product_id','=',stock.product_id.id),('pedimento_id','=',False)])
            if stock.pedimento_id:
                if stock.prorate_id:
                    prorate_id = [stock.prorate_id.id]
                stock_obj.write(cr, uid, stock_ids, {'pedimento_id':stock.pedimento_id.id})
                stockable_ids = stockable_line_pool.search(cr, uid, [('move_id','in',tuple(stock_ids))])
                stockable_line_pool.write(cr, uid, stockable_ids, {'pedimento_id':stock.pedimento_id.id})
        if prorate_id:
            stock_prorate.refresh_lines(cr, uid, prorate_id, context=None)
        return res
split_in_production_lot()

# Agregamos manejar una secuencia por cada tienda para controlar viajes 
class sale_order(osv.osv):
    _name = "sale.order"
    _inherit = "sale.order"
    _columns = {
    }

    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=None)
        for order in self.browse(cr, uid, ids, context=context):
            origin = order.name
            stock_obj = self.pool.get('stock.picking.out')
            lot_obj = self.pool.get('stock.production.lot.pedimento')
            stock_id = stock_obj.search(cr, uid, [('origin','=',origin)])
            for stock in stock_obj.browse(cr, uid, stock_id, context=None):
                stock_split_obj = self.pool.get('stock.move.split')
                for line in stock.move_lines:
                    qty_lines = line.product_qty
                    lot_disp = lot_obj.search(cr, uid, [('product_id','=',line.product_id.id),('stock_available','>',0.0)])
                    lot_disp = tuple(lot_disp)
                    product_id = line.product_id.id
                    move_lines_lots = []
                    if lot_disp:
                        cr.execute("select id from stock_production_lot_pedimento where id in %s order by date", (lot_disp,))
                        data_ids = [x[0] for x in cr.fetchall()]
                        cr.execute("select sum(stock_available) from stock_production_lot_pedimento where id in %s", (lot_disp,))
                        sum_lots_disp = cr.fetchall()[0][0]
                        while (qty_lines > 0.0):
                            if sum_lots_disp > 0:
                                for lote in lot_obj.browse(cr, uid, data_ids, context=None):
                                    qty_available = lote.stock_available
                                    qty_asign = 0.0
                                    if qty_lines > qty_available:
                                        qty_asign = qty_available
                                        qty_lines = qty_lines - qty_available
                                    elif qty_lines <= qty_available:
                                        qty_asign = qty_lines
                                        qty_lines = 0.0
                                    xline = (0,0,{
                                        'name': lote.name,
                                        'quantity': qty_asign,
                                        'pedimento_id': lote.id,
                                        })
                                    move_lines_lots.append(xline)
                                    stock_available_w = lote.stock_available - qty_asign
                                    lote.write({'stock_available':stock_available_w})
                                    sum_lots_disp = sum_lots_disp - qty_asign
                            else:
                                break
                        wizard_split = {
                                'qty': line.product_qty,
                                'product_id': line.product_id.id,
                                'product_uom': line.product_id.uom_id.id,
                                #'line_ids': [x for x in move_lines_lots],
                                'line_exist_ids': [x for x in move_lines_lots],
                                'use_exist' : True,
                                'location_id': line.location_id.id,
                                }
                        stock_split_id = stock_split_obj.create(cr, uid, wizard_split, context=None)
                        # for sp in stock_split_obj.browse(cr, uid, [stock_split_id], context=None):
                        #     print "############# CANTIDAD", sp.qty
                        #     print "############# producto", sp.product_id.id

                        # for xplit in stock_split_obj.browse(cr, uid, [stock_split_id], context=None):
                        #     for xln in xplit.line_exist_ids:
                        #         print "###################### PRODUCT QTY >>>>", xln.quantity
                        
                        stock_split_obj.split_especial(cr, uid, [stock_split_id], [line.id], context=context)
                        ##### BUSCAMOS LOS LOTES Y LOS ASIGNAMOS A LAS VENTAS DE PRODUCTOS QUE TENGAN PEDIMENTOS
                        # prodlot = self.pool.get('stock.production.lot').browse(cr, uid, data_ids, context=ctx)
        return  res
sale_order()

