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

class stock_partial_picking(osv.osv):
    _name = 'stock.partial.picking'
#     _inherit ='stock.partial.picking'
#     _columns = {
#     # 'pedimento_id': fields.many2one('pedimento.custom', 'Pedimento Aduanal'),
#     'picking_type': fields.char('Tipo de Picking', size=8),
#         }

#     # def _get_pedimento(self, cr, uid, context=None):
#     #     res = 0
#     #     active_model = context and context.get('active_model', False)
#     #     stock_picking = self.pool.get(active_model)
#     #     if active_model == 'stock.picking.in':
#     #         picking_ids = context.get('active_ids', [])
#     #         for picking in stock_picking.browse(cr, uid, picking_ids, context=None):
#     #             if picking.type == 'in':
#     #                 if picking.pedimento_id:
#     #                     res = int(picking.pedimento_id['id'])
#     #     return res

#     def _get_type(self, cr, uid, context=None):
#         tip = ""
#         active_model = context and context.get('active_model', False)
#         stock_picking = self.pool.get(active_model)
#         picking_ids = context.get('active_ids', [])
#         if not picking_ids:
#             return False
#         for picking in stock_picking.browse(cr, uid, picking_ids, context=None):
#             tip = picking.type
#         return tip

#     _defaults = {
#         # 'pedimento_id': _get_pedimento,
#         'picking_type': _get_type,
#         }

#     # def on_change_pedimento(self, cr, uid, ids, pedimento_id, move_ids, picking_id, picking_type, context=None):
#     #     res = {}
#     #     move_ids = move_ids
#     #     if picking_type == 'in':
#     #         if pedimento_id:
#     #             pedimento_obj = self.pool.get('pedimento.custom')
#     #             pedimento_br = pedimento_obj.browse(cr, uid, pedimento_id, context=None)
#     #             no_serie = pedimento_br.pedimento_sequence
#     #             stock_lot_obj = self.pool.get('stock.production.lot.pedimento')
#     #             stock_obj = self.pool.get('stock.picking.in')
#     #             product_ids = []
#     #             ## Se compone de id_product:id_lote  ejemplo producto coco id = 1 lote del producto 12 quedaria {1:12}
#     #             product_serie = {}

#     #             for stock in stock_obj.browse(cr, uid, [picking_id], context=None):
#     #                 for line in stock.move_lines:
#     #                     product_ids.append(line.product_id.id)
#     #             product_ids = set(product_ids)
#     #             for pr in product_ids:

#     #                 cr.execute("select sum(product_qty) from stock_move where picking_id=%s and product_id=%s", (picking_id,pr))
#     #                 pediment_qty = cr.fetchall()[0][0]
#     #                 vals = {'name':no_serie,'product_id':pr,'stock_available':0.0,'pedimento_id':pedimento_id}
#     #                 stock_lot_id = stock_lot_obj.search(cr, uid, [('name','=',no_serie),('product_id','=',pr)])
#     #                 if stock_lot_id:
#     #                     product_serie.update({pr:stock_lot_id[0]})
#     #                 else:
#     #                     stock_lot_id = stock_lot_obj.create(cr, uid, vals, context=None)
#     #                     product_serie.update({pr:stock_lot_id})
#     #             for line in move_ids:
#     #                 if len(line) >= 3:
#     #                     if type(line[2]) == type({}):
#     #                         if line[2].has_key('pedimento_id') == False or line[2]['pedimento_id'] == False :
#     #                             product_id_l = line[2]['product_id']
#     #                             lote = product_serie[product_id_l]
#     #                             line[2].update({'pedimento_id':lote})
#     #             res.update({'move_ids':move_ids})
#     #     return {'value':res}

#     # def do_partial(self, cr, uid, ids, context=None):
#     #     res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context)
#     #     stock_picking = self.pool.get('stock.picking')
#     #     stock_move = self.pool.get('stock.move')
#     #     picking_ids = context and context.get('active_ids', False)
#         # move_ids = []
#         # for rec in self.browse(cr, uid, ids, context=None):
#         #     if picking_ids:
#         #         if rec.picking_id.backorder_id:
#         #             picking_ids.append(rec.picking_id.backorder_id.id)
#         #     if rec.picking_id.type == 'in':
#         #         if rec.picking_id.backorder_id:
#         #             for move in rec.picking_id.backorder_id.move_lines:
#         #                 cr.execute("select pedimento_id from stock_move where picking_id=%s and product_id=%s", (picking_ids[0],move.product_id.id,))
#         #                 pedimento_id = cr.fetchall()
#         #                 if pedimento_id:
#         #                     move.write({'pedimento_id':pedimento_id[0][0]})

#         # return res

# stock_partial_picking()

class stock_partial_picking_line(osv.osv):
    _name = 'stock.partial.picking.line'
# #     _inherit ='stock.partial.picking.line'
# #     _columns = {
# #     'pedimento_id': fields.many2one('stock.production.lot.pedimento','No. Pedimento')
# #         }

# #     _default = {
# #         }

# #     def copy(self, cr, uid, id, default=None, context=None):
# #         # ref = self.pool.get('ir.sequence').get(cr, uid, 'pre.order.tpv')
# #         if not default:
# #             default = {}
# #         default.update({

# #                         'pedimento_id': False,
# #                         })
# #         return super(stock_partial_picking_line, self).copy(cr, uid, id, default, context=context)

# # stock_partial_picking_line()


class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit ='stock.picking'
    _columns = {
    'pedimento_id': fields.many2one('pedimento.custom', 'Pedimento Aduanal'),
        }

    _default = {
        }

    def copy(self, cr, uid, id, default=None, context=None):
        # ref = self.pool.get('ir.sequence').get(cr, uid, 'pre.order.tpv')
        if not default:
            default = {}

        default.update({

                        'pedimento_id': False,
                        })
        return super(stock_picking, self).copy(cr, uid, id, default, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        res = super(stock_picking, self).action_cancel(cr, uid, ids, context)
        pedimento_obj = self.pool.get('stock.production.lot.pedimento')
        for rec in self.browse(cr, uid, ids, context=None):
            for line in rec.move_lines:
                if line.pedimento_id:
                    new_pedimento_qty = line.pedimento_id.stock_available+line.product_qty
                    line.pedimento_id.write({'stock_available':new_pedimento_qty})
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(stock_picking, self).write(cr, uid, ids, vals, context=None)
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.backorder_id:
                for move in rec.backorder_id.move_lines:
                    cr.execute("select pedimento_id from stock_move where picking_id=%s and product_id=%s", (rec.id,move.product_id.id,))
                    pedimento_id = cr.fetchall()
                    if pedimento_id:
                        move.write({'pedimento_id':pedimento_id[0][0]})
        return res

    # def create(self, cr, uid, vals, context=None):
    #     type_picking = vals['type']
    #     s = super(stock_picking, self).create(cr, uid, vals, context=context)
    #     if type_picking == 'internal':
    #         picking_obj = self.pool.get('stock.picking')
    #     else:
    #         picking_obj = self.pool.get('stock.picking.'+type_picking)
    #     stock_move = self.pool.get('stock.move')
    #     move_ids = []
    #     stock_picking_back = picking_obj.search(cr, uid, [('backorder_id','=',s)])
    #     cr.execute("select id from stock_picking where backorder_id = %s" % s)
    #     if stock_picking_back:
    #         for picking in picking_obj.browse(cr, uid, stock_picking_back, context=None):
    #             if picking.backorder_id:
    #                 for move in picking.backorder_id.move_lines:
    #                     cr.execute("select pedimento_id from stock_move where picking_id=%s and product_id=%s", (picking.id,move.product_id.id,))
    #                     pedimento_id = cr.fetchall()
    #                     if pedimento_id:
    #                         move.write({'pedimento_id':pedimento_id[0][0]})

    #     return s
stock_picking()

# class stock_picking_in(osv.osv):
#     _name = 'stock.picking.in'
#     _inherit ='stock.picking.in'
#     _columns = {
#     'pedimento_id': fields.many2one('pedimento.custom', 'Pedimento Aduanal'),
#         }

#     _default = {
#         }

# stock_picking_in()

# class stock_picking_out(osv.osv):
#     _name = 'stock.picking.out'
#     _inherit ='stock.picking.out'
#     _columns = {
#     'pedimento_id': fields.many2one('pedimento.custom', 'Pedimento Aduanal'),
#         }

#     _default = {
#         }


# stock_picking_out()
