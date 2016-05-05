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


from openerp import netsvc
import time

from openerp.osv import osv,fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from datetime import date, datetime, timedelta

####### MODIFICACION PARA INVENTARIO PENDIENTE VALIDACION #########
# class stock_fill_inventory(osv.osv_memory):
#     _name = "stock.fill.inventory"
#     _inherit = "stock.fill.inventory"
#     _columns = {
#     }
#     _defaults = {
#     }

#     def fill_inventory(self, cr, uid, ids, context=None):
#         """ To Import stock inventory according to products available in the selected locations.
#         @param self: The object pointer.
#         @param cr: A database cursor
#         @param uid: ID of the user currently logged in
#         @param ids: the ID or list of IDs if we want more than one
#         @param context: A standard dictionary
#         @return:
#         """
#         if context is None:
#             context = {}

#         inventory_line_obj = self.pool.get('stock.inventory.line')
#         location_obj = self.pool.get('stock.location')
#         move_obj = self.pool.get('stock.move')
#         uom_obj = self.pool.get('product.uom')
#         if ids and len(ids):
#             ids = ids[0]
#         else:
#              return {'type': 'ir.actions.act_window_close'}
#         fill_inventory = self.browse(cr, uid, ids, context=context)
#         res = {}
#         res_location = {}

#         if fill_inventory.recursive:
#             location_ids = location_obj.search(cr, uid, [('location_id',
#                              'child_of', [fill_inventory.location_id.id])], order="id",
#                              context=context)
#         else:
#             location_ids = [fill_inventory.location_id.id]

#         res = {}
#         flag = False
#         if not fill_inventory.set_stock_zero:
#             date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#             date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
#             date_consult = date_strp + timedelta(days=1)
#             datas = {}
#             for location in location_ids:
#                 move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done')], context=context)
#                 cr.execute("""
#                     select product_id from stock_move where id in %s group by product_id;
#                     """,(tuple(move_ids),))
#                 cr_res = cr.fetchall()
#                 product_ids = [x[0] for x in cr_res if cr_res]
#                 ###### PRODUCTOS CON NUMERO DE SERIE >>>>>>>>>
#                 cr.execute("""
#                     select product_id from stock_move where id in %s and
#                     prodlot_id is not null group by product_id;
#                     """,(tuple(move_ids),))
#                 cr_res = cr.fetchall()
#                 product_wl_ids = [x[0] for x in cr_res if cr_res]
#                 cr.execute("""
#                     select product_id from stock_move where id in %s and
#                     product_id not in %s group by product_id;
#                     """,(tuple(move_ids), tuple(product_wl_ids),))
#                 cr_res = cr.fetchall()
#                 product_wol_ids = [x[0] for x in cr_res if cr_res]

#                 for product in product_wol_ids:
#                     prod_br = self.pool.get('product.product').browse(cr, uid, product, context)
#                     stock_qty_product = self.pool.get('stock.location')._product_get(cr, uid, fill_inventory.location_id.id, [prod_br.id], {'uom': prod_br.uom_id.id, 'to_date': date_consult, 'compute_child': False})[prod_br.id]
#                     data_val_create = {'product_id': product,
#                                         'location_id': location,
#                                         'product_qty': stock_qty_product,
#                                         'product_uom': prod_br.uom_id.id,
#                                         'prod_lot_id': False,
#                                         'inventory_id': context['active_ids'][0]}
#                     inventory_line_obj.create(cr, uid, data_val_create, context=context)
#                 res[location] = {}
#                 move_ids = move_obj.search(cr, uid, [('id','in',tuple(move_ids)),('product_id','not in',tuple(product_wol_ids))], context=context)
#                 local_context = dict(context)
#                 local_context['raise-exception'] = False
#                 for move in move_obj.browse(cr, uid, move_ids, context=context):
#                     lot_id = move.prodlot_id.id
#                     prod_id = move.product_id.id
#                     if move.location_dest_id.id != move.location_id.id:
#                         if move.location_dest_id.id == location:
#                             qty = uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)
#                         else:
#                             qty = -uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)

#                         if datas.get((prod_id, lot_id)):
#                             qty += datas[(prod_id, lot_id)]['product_qty']

#                         datas[(prod_id, lot_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': qty, 'product_uom': move.product_id.uom_id.id, 'prod_lot_id': lot_id}
#                 if datas:
#                     flag = True
#                     res[location] = datas

#                 if not flag:
#                     raise osv.except_osv(_('Error!'), _('Ningún producto en esta ubicación. Por favor seleccione una ubicación que contenga el Producto.'))

#         else:
#             for location in location_ids:
#                 datas = {}
#                 res[location] = {}
#                 move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done')], context=context)
#                 local_context = dict(context)
#                 local_context['raise-exception'] = False
#                 for move in move_obj.browse(cr, uid, move_ids, context=context):
#                     lot_id = move.prodlot_id.id
#                     prod_id = move.product_id.id
#                     if move.location_dest_id.id != move.location_id.id:
#                         if move.location_dest_id.id == location:
#                             qty = uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)
#                         else:
#                             qty = -uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)


#                         if datas.get((prod_id, lot_id)):
#                             qty += datas[(prod_id, lot_id)]['product_qty']

#                         datas[(prod_id, lot_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': qty, 'product_uom': move.product_id.uom_id.id, 'prod_lot_id': lot_id}

#                 if datas:
#                     flag = True
#                     res[location] = datas

#             if not flag:
#                 raise osv.except_osv(_('Error!'), _('Ningún producto en esta ubicación. Por favor seleccione una ubicación que contenga el Producto.'))

#         for stock_move in res.values():
#             for stock_move_details in stock_move.values():
#                 stock_move_details.update({'inventory_id': context['active_ids'][0]})
#                 domain = []
#                 for field, value in stock_move_details.items():
#                     if field == 'product_qty' and fill_inventory.set_stock_zero:
#                          domain.append((field, 'in', [value,'0']))
#                          continue
#                     domain.append((field, '=', value))

#                 if fill_inventory.set_stock_zero:
#                     stock_move_details.update({'product_qty': 0})

#                 line_ids = inventory_line_obj.search(cr, uid, domain, context=context)

#                 if not line_ids:
#                     inventory_line_obj.create(cr, uid, stock_move_details, context=context)

#         return {'type': 'ir.actions.act_window_close'}

# stock_fill_inventory()

# ######### HERENCIA DE FACTURACION DESDE ALBARANES ##############
# class stock_partial_picking(osv.osv):
#     _name = 'stock.partial.picking'
#     _inherit ='stock.partial.picking'
#     _columns = {
#         }

#     def do_partial(self, cr, uid, ids, context=None):
#         for rec in self.browse(cr, uid, ids, context=None):
#             if not rec.move_ids:
#                 raise osv.except_osv(_('Error!'),
#                     _('Debes recibir o enviar al menos 1 producto.'))

#         res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context)

#         return res

# stock_partial_picking()

class stock_return_picking(osv.osv_memory):
    _name = 'stock.return.picking'
    _inherit ='stock.return.picking'
    _columns = {
        }

    _defaults = {
        }

    def create_returns(self, cr, uid, ids, context=None):
        """
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.memory')
        act_obj = self.pool.get('ir.actions.act_window')
        model_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0

#        Create new picking for returned products

        seq_obj_name = 'stock.picking'
        new_type = 'internal'
        if pick.type =='out':
            new_type = 'in'
            seq_obj_name = 'stock.picking.in'
        elif pick.type =='in':
            new_type = 'out'
            seq_obj_name = 'stock.picking.out'
        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        new_picking = pick_obj.copy(cr, uid, pick.id, {
                                        'name': _('%s-%s-return') % (new_pick_name, pick.name),
                                        'move_lines': [],
                                        'state':'draft',
                                        'type': new_type,
                                        'date':date_cur,
                                        'invoice_state': data['invoice_state'],
        })

        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            if not mov_id:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            new_location = move.location_dest_id.id
            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            if returned_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                returned_lines += 1
                new_move=move_obj.copy(cr, uid, move.id, {
                                            'product_qty': new_qty,
                                            'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                            'picking_id': new_picking,
                                            'state': 'draft',
                                            'location_id': new_location,
                                            'location_dest_id': move.location_id.id,
                                            'date': date_cur,
                })
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4,new_move)]}, context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        # Update view id in context, lp:702939
        model_list = {
                'out': 'stock.picking.out',
                'in': 'stock.picking.in',
                'internal': 'stock.picking',
        }
        ################ CHERMAN ###################
        #### SI EL ALBARAN DEVUELTO SIGUE EN PARA FACTURAR CAMBIAMOS A NO APLICABLE MANUALMENTE
        if pick.invoice_state == '2binvoiced':
            pick.write({'invoice_state':'none'})
        return {
            'domain': "[('id', 'in', ["+str(new_picking)+"])]",
            'name': _('Returned Picking'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model': model_list.get(new_type, 'stock.picking'),
            'type':'ir.actions.act_window',
            'context':context,
        }
