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


from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def do_partialxxx(self, cr, uid, ids, partial_datas, context=None):
        print "- - - - - - - - - - - - - - - - - - -"
        print "Clase stock_picking, Metodo: do_partial"

        """ Makes partial picking and moves done.
        @param partial_datas : Dictionary containing details of partial picking
                          like partner_id, partner_id, delivery_date,
                          delivery moves with product_id, product_qty, uom
        @return: Dictionary of values
        """
        if context is None:
            context = {}
        else:
            context = dict(context)
        res = {}
        move_obj = self.pool.get('stock.move')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        sequence_obj = self.pool.get('ir.sequence')
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids, context=context):
            new_picking = None
            complete, too_many, too_few = [], [], []
            move_product_qty, prodlot_ids, product_avail, partial_qty, uos_qty, product_uoms = {}, {}, {}, {}, {}, {}
            for move in pick.move_lines:
                if move.state in ('done', 'cancel'):
                    continue
                partial_data = partial_datas.get('move%s'%(move.id), {})
                product_qty = partial_data.get('product_qty',0.0)
                move_product_qty[move.id] = product_qty
                product_uom = partial_data.get('product_uom', move.product_uom.id)
                product_price = partial_data.get('product_price', move.purchase_line_id and move.purchase_line_id.price_unit or 0.0)
                product_currency = partial_data.get('product_currency', move.purchase_line_id and move.purchase_line_id.order_id.pricelist_id.currency_id.id or False)
                prodlot_id = partial_data.get('prodlot_id')
                prodlot_ids[move.id] = prodlot_id
                product_uoms[move.id] = product_uom
                partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                uos_qty[move.id] = partial_qty[move.id] #uom_obj._compute_uos_qty(product_uom, product_qty, move.product_uos) if product_qty else 0.0
                if move.product_qty == partial_qty[move.id]:
                    complete.append(move)
                elif move.product_qty > partial_qty[move.id]:
                    too_few.append(move)
                else:
                    too_many.append(move)

                # Average price computation
                if (pick.type in ('in','out')) and (move.product_id.cost_method == 'average'):
                    product = product_obj.browse(cr, uid, move.product_id.id)
                    move_currency_id = move.company_id.currency_id.id
                    context['currency_id'] = move_currency_id
                    qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                    print "qty: ", qty
                    if product.id not in product_avail:
                        # keep track of stock on hand including processed lines not yet marked as done
                        print "Entrando a Product "
                        product_avail[product.id] = product.qty_available
                    print "pick.type: ", pick.type
                    if qty > 0 and pick.type=='in':
                        new_price = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, product_price, round=False)
                        print "new_price desde currency_obj.compute: ", new_price                        
                        new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                product.uom_id.id)
                        print "new_price desde uom_obj._compute_price: ", new_price
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            print "amount_unit: ", amount_unit
                            print "product.qty_available: ", product.qty_available
                            print "(amount_unit * product.qty_available) : ", amount_unit * product.qty_available
                            print "(new_price * qty) : ", (new_price * qty)
                            print "((amount_unit * product.qty_available) + (new_price * qty)): ", ((amount_unit * product.qty_available) + (new_price * qty))
                            print "(product.qty_available + qty) : ", (product.qty_available + qty)
                            print "((amount_unit * product.qty_available) + (new_price * qty))/(product.qty_available + qty) : ", ((amount_unit * product.qty_available) + (new_price * qty))/(product.qty_available + qty)
                            
                            new_std_price = ((amount_unit * product_avail[product.id])\
                                + (new_price * qty))/(product_avail[product.id] + qty)
                            
                            #new_std_price = ((amount_unit * product.qty_available)\
                            #    + (new_price * qty))/(product.qty_available + qty)
                            print "Actualizando costo promedio 1"
                            print "new_std_price: ", new_std_price
                        # Write the field according to price type field
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})
                        
                        product_avail[product.id] += qty
                        
                    elif qty > 0 and pick.type=='out' and move.purchase_line_id:
                        new_price1 = currency_obj.compute(cr, uid, product_currency,
                                move_currency_id, move.purchase_line_id.price_unit, round=True)
                        new_price2 = uom_obj._compute_price(cr, uid, product_uom, new_price1,
                                product.uom_id.id)
                        if product_avail[product.id] <= 0:
                            product_avail[product.id] = 0
                            new_std_price = new_price
                        else:
                            # Get the standard price
                            amount_unit = product.price_get('standard_price', context=context)[product.id]
                            print "amount_unit: ", amount_unit
                            print "product.qty_available: ", product.qty_available
                            print "(amount_unit * product.qty_available) : ", amount_unit * product.qty_available
                            print "(new_price * qty) : ", (new_price * qty)
                            print "((amount_unit * product.qty_available) + (new_price * qty)): ", ((amount_unit * product.qty_available) + (new_price * qty))
                            print "(product.qty_available + qty) : ", (product.qty_available + qty)
                            print "((amount_unit * product.qty_available) + (new_price * qty))/(product.qty_available + qty) : ", ((amount_unit * product.qty_available) + (new_price * qty))/(product.qty_available + qty)

                            new_std_price = (((amount_unit * product_avail[product.id]) - (qty * new_price2)) \
                                    / (product_avail[product.id] - qty)) if (product_avail[product.id] - qty) else 0.0
                            print "new_std_price: ", new_std_price
                        # Write the field according to price type field
                        print "Actualizando costo promedio 2"
                        print "new_std_price: ", new_std_price
                        product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})

                        # Record the values that were chosen in the wizard, so they can be
                        # used for inventory valuation if real-time valuation is enabled.
                        move_obj.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency})

                    
            # every line of the picking is empty, do not generate anything
            empty_picking = not any(q for q in move_product_qty.values() if q > 0)

            for move in too_few:
                product_qty = move_product_qty[move.id]
                if not new_picking and not empty_picking:
                    new_picking_name = pick.name
                    self.write(cr, uid, [pick.id], 
                               {'name': sequence_obj.get(cr, uid,
                                            'stock.picking.%s'%(pick.type)),
                               })
                    pick.refresh()
                    new_picking = self.copy(cr, uid, pick.id,
                            {
                                'name': new_picking_name,
                                'move_lines' : [],
                                'state':'draft',
                                'invoice_state' : pick.invoice_state,
                            })
                if product_qty != 0:
                    defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': uos_qty[move.id],
                            'picking_id' : new_picking,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids[move.id]
                    if prodlot_id:
                        defaults.update(prodlot_id=prodlot_id)
                    move_obj.copy(cr, uid, move.id, defaults)
                move_obj.write(cr, uid, [move.id],
                        {
                            'product_qty': move.product_qty - partial_qty[move.id],
                            'product_uos_qty': move.product_uos_qty - uos_qty[move.id],
                            'prodlot_id': False,
                            'tracking_id': False,
                        })

            if new_picking:
                move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
            for move in complete:
                defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                if prodlot_ids.get(move.id):
                    defaults.update({'prodlot_id': prodlot_ids[move.id]})
                move_obj.write(cr, uid, [move.id], defaults)
            for move in too_many:
                product_qty = move_product_qty[move.id]
                defaults = {
                    'product_qty' : product_qty,
                    'product_uos_qty': uos_qty[move.id],
                    'product_uom': product_uoms[move.id]
                }
                prodlot_id = prodlot_ids.get(move.id)
                if prodlot_ids.get(move.id):
                    defaults.update(prodlot_id=prodlot_id)
                if new_picking:
                    defaults.update(picking_id=new_picking)
                move_obj.write(cr, uid, [move.id], defaults)

            # At first we confirm the new picking (if necessary)
            if new_picking:
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                # Then we finish the good picking
                self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                self.action_move(cr, uid, [new_picking], context=context)
                wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                delivered_pack_id = new_picking
                self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (pick.name), context=context)
            elif empty_picking:
                delivered_pack_id = pick.id
            else:
                self.action_move(cr, uid, [pick.id], context=context)
                wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                delivered_pack_id = pick.id

            delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
            res[pick.id] = {'delivered_picking': delivered_pack.id or False}
        #raise osv.except_osv('Pausa !', 'Hacemos una pausa en Stock Picking...')
        print "Saliendo"
        print "res: ", res
        return res

    
    
    
class stock_move(osv.osv):
    _inherit = 'stock.move'

    def _create_product_valuation_moves(self, cr, uid, move, context=None):
        """
        Generate the appropriate accounting moves if the product being moves is subject
        to real_time valuation tracking, and the source or destination location is
        a transit location or is outside of the company.
        """
        if move.product_id.valuation == 'real_time': # FIXME: product valuation should perhaps be a property?
            if context is None:
                context = {}
            src_company_ctx = dict(context,force_company=move.location_id.company_id.id)
            dest_company_ctx = dict(context,force_company=move.location_dest_id.company_id.id)
            account_moves = []
            # Outgoing moves (or cross-company output part)
            if move.location_id.company_id \
                and (move.location_id.usage == 'internal' and move.location_dest_id.usage != 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, src_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #returning goods to supplier
                if move.location_dest_id.usage == 'supplier':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_src, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_valuation, acc_dest, reference_amount, reference_currency_id, context))]
            # Incoming moves (or cross-company input part)
            if move.location_dest_id.company_id \
                and (move.location_id.usage != 'internal' and move.location_dest_id.usage == 'internal'\
                     or move.location_id.company_id != move.location_dest_id.company_id):
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation(cr, uid, move, dest_company_ctx)
                reference_amount, reference_currency_id = self._get_reference_accounting_values_for_valuation(cr, uid, move, src_company_ctx)
                #goods return from customer
                if move.location_id.usage == 'customer':
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_dest, acc_valuation, reference_amount, reference_currency_id, context))]
                else:
                    account_moves += [(journal_id, self._create_account_move_line(cr, uid, move, acc_src, acc_valuation, reference_amount, reference_currency_id, context))]

            move_obj = self.pool.get('account.move')
            for j_id, move_lines in account_moves:
                xdate = context.get('date', fields.date.context_today(self,cr,uid,context=context))
                for x in move_lines:
                    x[2]['date'] = xdate
                _move = {
                        'period_id' : move_obj._get_period(cr, uid,context=context),
                        'date'              : xdate,
                         'journal_id': j_id,
                         'line_id': move_lines,
                         'ref': move.picking_id and move.picking_id.name}
                move_obj.create(cr, uid,
                        {
                        'period_id' : move_obj._get_period(cr, uid,context=context),
                        'date'              : xdate,
                         'journal_id': j_id,
                         'line_id': move_lines,
                         'ref': move.picking_id and move.picking_id.name}, context=context)
            return

        
    def _get_reference_accounting_values_for_valuation(self, cr, uid, move, context=None):
        """
        Return the reference amount and reference currency representing the inventory valuation for this move.
        These reference values should possibly be converted before being posted in Journals to adapt to the primary
        and secondary currencies of the relevant accounts.
        """
        product_uom_obj = self.pool.get('product.uom')

        # by default the reference currency is that of the move's company
        reference_currency_id = move.company_id.currency_id.id

        default_uom = move.product_id.uom_id.id
        qty = product_uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, default_uom)
        #print "qty: ", qty
        # if product is set to average price and a specific value was entered in the picking wizard,
        # we use it
        
        # Revisamos si es una Entrada/Devolucion de Pedido de compra
        if move.product_id.cost_method == 'average' and move.picking_id and move.picking_id.purchase_id and move.price_unit: 
            reference_amount = move.price_unit * move.product_qty #qty * move.price_unit
            reference_currency_id = move.price_currency_id.id or reference_currency_id
            
        elif move.location_dest_id.usage != 'internal' and move.product_id.cost_method == 'average':
            reference_amount = qty * move.product_id.standard_price
        elif move.product_id.cost_method == 'average' and move.price_unit:
            reference_amount = qty * move.price_unit
            reference_currency_id = move.price_currency_id.id or reference_currency_id

        # Otherwise we default to the company's valuation price type, considering that the values of the
        # valuation field are expressed in the default currency of the move's company.
        else:
            if context is None:
                context = {}
            currency_ctx = dict(context, currency_id = move.company_id.currency_id.id)
            amount_unit = move.product_id.price_get('standard_price', context=currency_ctx)[move.product_id.id]
            reference_amount = amount_unit * qty
        return reference_amount, reference_currency_id    
        

    def do_partialxxx(self, cr, uid, ids, partial_datas, context=None):
        """ Makes partial pickings and moves done.
        @param partial_datas: Dictionary containing details of partial picking
                          like partner_id, delivery_date, delivery
                          moves with product_id, product_qty, uom
        """
        res = {}
        picking_obj = self.pool.get('stock.picking')
        product_obj = self.pool.get('product.product')
        currency_obj = self.pool.get('res.currency')
        uom_obj = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")

        if context is None:
            context = {}

        complete, too_many, too_few = [], [], []
        move_product_qty = {}
        prodlot_ids = {}
        for move in self.browse(cr, uid, ids, context=context):
            if move.state in ('done', 'cancel'):
                continue
            partial_data = partial_datas.get('move%s'%(move.id), False)
            assert partial_data, _('Missing partial picking data for move #%s.') % (move.id)
            product_qty = partial_data.get('product_qty',0.0)
            move_product_qty[move.id] = product_qty
            product_uom = partial_data.get('product_uom',False)
            product_price = partial_data.get('product_price',0.0)
            product_currency = partial_data.get('product_currency',False)
            prodlot_ids[move.id] = partial_data.get('prodlot_id')
            if move.product_qty == product_qty:
                complete.append(move)
            elif move.product_qty > product_qty:
                too_few.append(move)
            else:
                too_many.append(move)

            # Average price computation
            if (move.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                product = product_obj.browse(cr, uid, move.product_id.id)
                move_currency_id = move.company_id.currency_id.id
                context['currency_id'] = move_currency_id
                qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
                print "qty: ", qty
                if qty > 0:
                    new_price = currency_obj.compute(cr, uid, product_currency,
                            move_currency_id, product_price, round=False)
                    print "new_price desde currency_obj.compute: ", new_price
                    new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                            product.uom_id.id)
                    print "new_price desde uom_obj._compute_price: ", new_price
                    if product.qty_available <= 0:
                        new_std_price = new_price
                    else:
                        # Get the standard price
                        amount_unit = product.price_get('standard_price', context=context)[product.id]
                        print "amount_unit: ", amount_unit
                        print "product.qty_available: ", product.qty_available
                        print "(amount_unit * product.qty_available) : ", amount_unit * product.qty_available
                        print "(new_price * qty) : ", (new_price * qty)
                        print "((amount_unit * product.qty_available) + (new_price * qty)): ", ((amount_unit * product.qty_available) + (new_price * qty))
                        print "(product.qty_available + qty) : ", (product.qty_available + qty)
                        print "((amount_unit * product.qty_available) + (new_price * qty))/(product.qty_available + qty) : ", ((amount_unit * product.qty_available) + (new_price * qty))/(product.qty_available + qty)
                        new_std_price = ((amount_unit * product.qty_available) + (new_price * qty))/(product.qty_available + qty)
                    print "new_std_price: ", new_std_price

                    product_obj.write(cr, uid, [product.id],{'standard_price': new_std_price})

                    # Record the values that were chosen in the wizard, so they can be
                    # used for inventory valuation if real-time valuation is enabled.
                    self.write(cr, uid, [move.id],
                                {'price_unit': product_price,
                                 'price_currency_id': product_currency,
                                })
                raise osv.except_osv('Pausa !', 'Hacemos una pausa en Stock Move...')
        for move in too_few:
            product_qty = move_product_qty[move.id]
            if product_qty != 0:
                defaults = {
                            'product_qty' : product_qty,
                            'product_uos_qty': product_qty,
                            'picking_id' : move.picking_id.id,
                            'state': 'assigned',
                            'move_dest_id': False,
                            'price_unit': move.price_unit,
                            }
                prodlot_id = prodlot_ids[move.id]
                if prodlot_id:
                    defaults.update(prodlot_id=prodlot_id)
                new_move = self.copy(cr, uid, move.id, defaults)
                complete.append(self.browse(cr, uid, new_move))
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty - product_qty,
                        'product_uos_qty': move.product_qty - product_qty,
                        'prodlot_id': False,
                        'tracking_id': False,
                    })


        for move in too_many:
            self.write(cr, uid, [move.id],
                    {
                        'product_qty': move.product_qty,
                        'product_uos_qty': move.product_qty,
                    })
            complete.append(move)

        for move in complete:
            if prodlot_ids.get(move.id):
                self.write(cr, uid, [move.id],{'prodlot_id': prodlot_ids.get(move.id)})
            self.action_done(cr, uid, [move.id], context=context)
            if  move.picking_id.id :
                # TOCHECK : Done picking if all moves are done
                cr.execute("""
                    SELECT move.id FROM stock_picking pick
                    RIGHT JOIN stock_move move ON move.picking_id = pick.id AND move.state = %s
                    WHERE pick.id = %s""",
                            ('done', move.picking_id.id))
                res = cr.fetchall()
                if len(res) == len(move.picking_id.move_lines):
                    picking_obj.action_move(cr, uid, [move.picking_id.id])
                    wf_service.trg_validate(uid, 'stock.picking', move.picking_id.id, 'button_done', cr)

        return [move.id for move in complete]
    
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: