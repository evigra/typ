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
from datetime import date, datetime, time, timedelta


class stock_partial_picking(osv.osv):
    _name = 'stock.partial.picking'
    _inherit ='stock.partial.picking'
    _columns = {
        }

    def do_partial(self, cr, uid, ids, context=None):
        res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context)
        stock_picking = self.pool.get('stock.picking')
        purchase_obj = self.pool.get('purchase.order')
        stock_move = self.pool.get('stock.move')
        picking_ids = []
        picking_ids = context and context.get('active_ids', False)
        # if active_ids != None:
        #     picking_ids.append(active_ids[0])      
        picking_invoice_line = []
        purchase_ids = []

        for rec in self.browse(cr, uid, ids, context=None):
            # if not picking_ids:
            #     picking_ids.append(rec.picking_id.id)
            picking_browse = stock_picking.browse(cr, uid, picking_ids, context=None)[0]
            origin = picking_browse.origin
            if picking_browse.type != 'internal':
                if picking_browse.origin:
                    if ':' in origin:
                        origin = tuple(origin.split(':'))
                        purchase_ids = purchase_obj.search(cr, uid, [('name','in',origin)])
                    else:
                        purchase_ids = purchase_obj.search(cr, uid, [('name','=',origin)])
                    if origin:
                        
                        if purchase_ids:
                            for ln in rec.move_ids:
                                xline = {
                                'product_id': ln.product_id.id,
                                'product_qty': ln.quantity,
                                'prodlot_id': ln.prodlot_id.id,
                                # 'pedimento_id': ln.pedimento_id.id,
                                'picking_id': picking_browse.backorder_id.id if picking_browse.backorder_id else picking_ids[0],
                                'order_id': purchase_ids[0],
                                }
                                self.pool.get('picking.invoice.received').create(cr, uid, xline, context)
                        #     picking_invoice_line.append(xline)
                        # if invoice_ids:
                        #     invoice_obj.write(cr, uid, invoice_ids, {'products_received_line':[x for x in picking_invoice_line]})
                    cur_obj=self.pool.get('res.currency')
                    tax_obj = self.pool.get('account.tax')
                    line_obj = self.pool.get('purchase.order.line')
                    for purchase in purchase_obj.browse(cr, SUPERUSER_ID, purchase_ids, context=None):
                        order_id = purchase.id
                        margin = 0.0
                        qty_product_lines = 0.0
                        for line in purchase.order_line:
                            qty_product_lines += line.product_qty
                        qty_received = 0.0
                        for line_r in purchase.products_received_line:

                            amount_receipt = 0.0
                            cr.execute("select price_unit from purchase_order_line where order_id=%s and product_id=%s" %(order_id,line_r.product_id.id))
                            cr_res = cr.fetchall()
                            price_unit = cr_res[0][0] if cr_res else 0.0
                            cr.execute("select id from purchase_order_line where order_id=%s and product_id=%s" %(order_id,line_r.product_id.id))
                            cr_res = cr.fetchall()
                            purchase_line_id = cr_res[0][0] if cr_res else False
			    if purchase_line_id:
                                line_br = line_obj.browse(cr, uid, purchase_line_id, context=None)
                                taxes = tax_obj.compute_all(cr, uid, line_br.taxes_id, line_br.price_unit, line_r.product_qty, line_br.product_id, line_br.order_id.partner_id)
                                cur = line_br.order_id.pricelist_id.currency_id
                                amount_receipt = cur_obj.round(cr, uid, cur, taxes['total_included'])

                                line_r.write({'amount_total':amount_receipt})
                                qty_received += line_r.product_qty
                        if qty_product_lines > 0.0 and qty_received > 0.0:
                            margin = (float(qty_received)/float(qty_product_lines))*100
                        purchase.write({'margin_products_receive':margin})
        return res

stock_partial_picking()
