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
from openerp import _
from openerp import SUPERUSER_ID

class update_date_stock(osv.osv_memory):
    _name = 'update.date.stock'
    _description = 'Actualizacion de Fechas de Arribo'
    _columns = {
        'datetime': fields.date('Fecha/Hora Actualizada', help='Define la Nueva Fecha/Hora', required=True),
    }
    _defaults = {  
      'datetime': lambda *a: datetime.now().strftime('%Y-%m-%d')
        }

    def update_fields_date(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', False)
        active_model = context and context.get('active_model', False)
        purchase_obj = self.pool.get('purchase.order')
        for rec in self.browse(cr, uid, ids, context=None):
            if active_model == 'stock.picking.in':
                stock_picking_obj = self.pool.get('stock.picking.in')
                for stock in stock_picking_obj.browse(cr, uid, active_ids, context=None):
                    if stock.state not in ('done','cancel'):
                        for move in stock.move_lines:
                            move.write({'date_expected':rec.datetime,'date':rec.datetime})
                    else:
                        raise osv.except_osv(
                            _('Error !'),
                            _('El Albaran %s esta Cancelado y/ó Recibido') % (stock.name,))

                    stock.write({'min_date':rec.datetime})
                    purchase_id = stock.purchase_id
                    if purchase_id:
                        purchase_id.write({'minimum_planned_date':rec.datetime})
            elif active_model == 'stock.move':
                stock_move_obj = self.pool.get('stock.move')
                picking_ids = []
                move_ids = []
                for move in stock_move_obj.browse(cr, uid, active_ids, context=None):
                    if move.state not in ('done','cancel'):
                        move.write({'date_expected':rec.datetime,'date':rec.datetime})
                        picking_ids.append(move.picking_id.id)
                        move_ids.append(move.id)
                    else:
                        raise osv.except_osv(
                            _('Error !'),
                            _('El Movimiento a Recibir %s esta Cancelado y/ó Recibido') % (move.name,))
                stock_picking_obj = self.pool.get('stock.picking.in')
                picking_ids = set(picking_ids)
                move_ids = set(move_ids)
                for pk in picking_ids:
                    cr.execute("select date_expected from stock_move where picking_id = %s and id in %s order by date_expected limit 1", (pk,tuple(move_ids),))
                    date_cr = cr.fetchone()
                    stock_picking_obj = self.pool.get('stock.picking.in')
                    stock_pick_b = stock_picking_obj.browse(cr, uid, [pk], context=None)[0]
                    purchase_id = purchase_obj.search(cr, uid, [('name','=',stock_pick_b.origin)])
                    if purchase_id:
                        purchase_obj.write(cr, uid, purchase_id, {'minimum_planned_date':rec.datetime})
            else:
                purchase_obj = self.pool.get('purchase.order')
                purchase_obj.write(cr, uid, active_ids, {'minimum_planned_date':rec.datetime}, context=None)
                purchase_br = purchase_obj.browse(cr, uid, active_ids, context=None)
                name_reference = [x.name for x in purchase_br]
                purchase_state = {}
                [purchase_state.update({str(x.name):str(x.state)}) for x in purchase_br]
                for purchase in purchase_state:
                    if purchase_state[purchase] in ('cancel','done'):
                        raise osv.except_osv(
                                    _('Error !'),
                                    _('El Pedido de Compra %s esta Cancelado y/ó Finalizado') % (purchase,))
                stock_picking_obj = self.pool.get('stock.picking.in')
                #picking_ids = stock_picking_obj.search(cr, uid, [('origin','in',tuple(name_reference))])
                picking_ids = stock_picking_obj.search(cr, uid, [('purchase_id','in',tuple(active_ids))])
                if picking_ids:
                    for pick in self.pool.get('stock.picking.in').browse(cr, uid, picking_ids, context):
                        if pick.state in ('done','cancel'):
                            raise osv.except_osv(
                                _('Error !'),
                                _('El Albaran %s esta Cancelado y/ó Recibido') % (pick.name,))

                    stock_picking_obj.write(cr, uid, picking_ids, {'min_date':rec.datetime+ ' 18:00:00'} )
        return True

update_date_stock()