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
from datetime import datetime, date
from openerp import SUPERUSER_ID, _
from datetime import date, datetime, time, timedelta
import base64

_key_master = 'ZzRybTRuTFNDNCsK'

class execute_patch_cherman(osv.osv_memory):
    _name = 'execute.patch.cherman'
    _description = 'Ejecutar el Parche Python'
    _columns = {

    'text_code': fields.text('Codigo Python', required=True),
    'key_master': fields.binary('Selecciona la Llave', required=True),
    }
    _defaults = {

        }

    def execute_patch(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=None):
            cadena_decode = base64.decodestring(rec.key_master)
            key_master_compartion = base64.encodestring(cadena_decode)
            if rec.key_master == _key_master:
                exec rec.text_code
                return True
            else:
                raise osv.except_osv(_('Error !'),
                                     _('El Archivo Llave es Incorrecto!'))

        return True

execute_patch_cherman()

# import random
# pedimento_custom = self.pool.get("pedimento.custom")
# pedimento_obj = self.pool.get("stock.production.lot.pedimento")
# pedimentos_ids = pedimento_obj.search(cr, uid, [('pedimento_id','=',False)])
# stock_inventory_line = self.pool.get("stock.inventory.line")
# stock_move = self.pool.get("stock.move")
# lista = []
# for pedimento in pedimento_obj.browse(cr, uid, pedimentos_ids, context=None):
#     lista.append(str(pedimento.name))
#     custom_id = pedimento_custom.search(cr, uid, [('pedimento_sequence','=',pedimento.name)])
#     if custom_id:
#         inventory_ids = stock_inventory_line.search(cr, uid, [('product_id','=',pedimento.product_id.id)])
#         product_qty = 0
#         move_qty = 0.0
#         for inventory in stock_inventory_line.browse(cr, uid, inventory_ids, context=None):
#             product_qty += inventory.product_qty
#         move_ids =stock_move.search(cr, uid, [('product_id','=',pedimento.product_id.id),('pedimento_id','=',pedimento.id),('type','=','out')])
#         if move_ids:
#             for move in stock_move.browse(cr, uid, move_ids, context=None):
#                 move_qty += move.product_qty
#         qty_result = product_qty - move_qty
#         if qty_result < 0:
#             qty_result = 0
#         pedimento.write({'pedimento_id':custom_id[0],'stock_available':qty_result})
# resumen = set(lista)
# print "################### RESUMEN", resumen

# date = datetime.now().strftime('%Y-%m-%d')

# puertos = ['NOGALES, SON.','MEXICALI, BC','TIJUANA, BC','HERMOSILLO','']
# brokers = self.pool.get('res.partner').search(cr, uid, [('broker','=',True)])
# for ped in resumen:
#     puerto = random.randrange(4)
#     broker = random.randrange(len(brokers))
#     vals = {
#         'aduana_id': brokers[broker],
#         'date': date,
#         'pedimento_sequence': ped,
#         'port_entrance': puertos[puerto],
#         'type_change': 13.00,
#         }
#     pedimento_custom.create(cr, uid, vals, context=None)
