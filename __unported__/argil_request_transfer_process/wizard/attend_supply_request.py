# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc
# import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
# from openerp import pooler
# from openerp.osv.orm import browse_record, browse_null
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP


class attend_supply_request(osv.osv_memory):
    _inherit = "attend.supply.request"
    _columns = {
        'supply_request_pur_line_ids': fields.one2many('attend.request.purchase.line','wiz_id','Purchase Requests'),
    }
    
    def get_missing_product_qty(self, cr, uid, product_data, product, warehouse_id,to_uom_id, context=None):
        res = super(attend_supply_request, self).get_missing_product_qty(cr, uid, 
                                            product_data,product, warehouse_id,to_uom_id, context)
        transfer_line_pool = self.pool.get('stock.transfer.line')
        uom_pool = self.pool.get('product.uom')
        transfer_line_ids = transfer_line_pool.search(cr, uid,[('transfer_id.state','=','draft'),
                                                               ('product_id','=',product.id),
                                                               ('transfer_id.warehouse_id','=',warehouse_id)])
        #TODO: need to consider the UOM
        total_qty = 0.0
        for line in transfer_line_pool.read(cr, uid, transfer_line_ids,['qty','product_uom']):
            total_qty += uom_pool._compute_qty(cr, uid, line['product_uom'][0], line['qty'], to_uom_id)
        res.update({'v_avail': res['v_avail'] - total_qty})
        return res
    
    def button_goto_phase2(self,cr, uid, ids, context=None):
        wiz_pur_line_pool = self.pool.get('attend.request.purchase.line')
        res =  super(attend_supply_request, self).button_goto_phase2(cr, uid, ids, context)
        wiz_obj = self.browse(cr, uid, ids, context)[0] 
        pur_line_ids = wiz_pur_line_pool.search(cr, uid, [('wiz_id','=',wiz_obj.id)])
        if pur_line_ids:
            wiz_pur_line_pool.unlink(cr, uid, pur_line_ids)
        for line in wiz_obj.supply_request_line_ids:
            diff_qty = line.qty_request - line.qty_to_send
            if diff_qty:
                wiz_pur_line_pool.create(cr, uid, {
                    'wiz_id':wiz_obj.id,
                    'supply_req_id':line.supply_req_id.id or False,
                    'product_id': line.product_id.id or False,
                    'product_uom_id':line.product_uom_id.id or False,
                    'qty_request':diff_qty,
                    'required_date': line.required_date or False,
                    'from_warehouse_id': line.from_warehouse_id.id or False,
                    'process_type':'draft',
                    'use_old_supply_request': line.qty_request == diff_qty or False
                    
                })
        return res
    
    def trasfer_line_data(self, cr, uid, ids,wiz_obj,wiz_line, context=None):
        return {
#                     'transfer_id':wiz_obj.transfer_id.id or False,
            'product_id': wiz_line.product_id.id or False,
            'supply_req_id': wiz_line.supply_req_id.id or 0,
            'product_uom':wiz_line.product_uom_id.id or False,
            'qty': wiz_line.qty_to_send or 0.0,
            'origin_qty':wiz_line.qty_request or 0.0,
            'standard_price':wiz_line.product_id.standard_price,
            'standard_price_dummy':wiz_line.product_id.standard_price,
            'dest_move_id':wiz_line.supply_req_id.dest_move_id.id or 0 
        }
    def _get_purchase_schedule_date(self, cr, uid, date_planned, company, context=None):
        
        new_date_planned = datetime.strptime(date_planned, DEFAULT_SERVER_DATETIME_FORMAT)
        schedule_date = (new_date_planned - relativedelta(days=company.po_lead))
        return schedule_date

    def _get_purchase_order_date(self, cr, uid, product, company, schedule_date, context=None):
        
        seller_delay = int(product.seller_delay)
        return schedule_date - relativedelta(days=seller_delay)
    
    def create_purchases(self, cr, uid, ids, wiz_obj,product_dict, context=None):
        product_obj = self.pool.get('product.product')
        partner_obj = self.pool.get('res.partner')
        uom_obj = self.pool.get('product.uom')
        pricelist_obj = self.pool.get('product.pricelist')
        acc_pos_obj = self.pool.get('account.fiscal.position')
        seq_obj = self.pool.get('ir.sequence')
        for line in product_dict:
            product = product_obj.browse(cr, uid, line['product_id'],)
            partner = product.seller_id
            #seller_qty = procurement.product_id.seller_qty
            if not partner:
                raise osv.except_osv(_('Error!'), _('Supplier not defined for the product %s.'% line.product_id.name))
            partner_id = partner.id
            address_id = partner_obj.address_get(cr, uid, [partner_id], ['delivery'])['delivery']
            pricelist_id = partner.property_product_pricelist_purchase.id
            uom_id = product.uom_po_id.id

            qty = uom_obj._compute_qty(cr, uid, line['product_uom'], line['product_qty'], uom_id)
#             if seller_qty:
#                 qty = max(qty,seller_qty)
            price = pricelist_obj.price_get(cr, uid, [pricelist_id], product.id, qty, partner_id, {'uom': uom_id})[pricelist_id]

            schedule_date = self._get_purchase_schedule_date(cr, uid, 
                    line['date_planned'], wiz_obj.company_id, context=context)
            purchase_date = self._get_purchase_order_date(cr, uid, product, wiz_obj.company_id, schedule_date, context=context)

            #Passing partner_id to context for purchase order line integrity of Line name
            new_context = context.copy()
            new_context.update({'lang': partner.lang, 'partner_id': partner_id})

            product = product_obj.browse(cr, uid, line['product_id'], context=new_context)
            taxes_ids = product.supplier_taxes_id
            taxes = acc_pos_obj.map_tax(cr, uid, partner.property_account_position, taxes_ids)

            name = product.partner_ref
            if product.description_purchase:
                name += '\n'+ product.description_purchase
            line_vals = {
                'name': name,
                'product_qty': qty,
                'product_id': line['product_id'],
                'product_uom': uom_id,
                'price_unit': price or 0.0,
                'date_planned': schedule_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
#                 'move_dest_id': res_id,
                'taxes_id': [(6,0,taxes)],
            }
            name = seq_obj.get(cr, uid, 'purchase.order') or _('PO: %s') % 'From Supply Request'
            po_vals = {
                'name': name,
                'origin': line['origin'],
                'partner_id': partner_id,
                'location_id': wiz_obj.warehouse_id.lot_stock_id.id,
                'warehouse_id': wiz_obj.warehouse_id.id,
                'pricelist_id': pricelist_id,
                'date_order': purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                'company_id': wiz_obj.company_id.id,
                'fiscal_position': partner.property_account_position and partner.property_account_position.id or False,
                'payment_term_id': partner.property_supplier_payment_term.id or False,
            }
            po_vals.update({'order_line': [(0,0,line_vals)]})
            self.pool.get('purchase.order').create(cr, uid, po_vals, context=context)
        return True
    
    def button_process_request(self, cr, uid, ids, context=None):
#         wiz_pur_line_pool = self.pool.get('attend.request.purchase.line')
#         wiz_line_pool = self.pool.get('attend.request.purchase.line')
        transfer_line_pool = self.pool.get('stock.transfer.line')
        transfer_pool = self.pool.get('stock.transfer')
        request_pool = self.pool.get('stock.supply_request')
        uom_pool = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")
        res =  super(attend_supply_request, self).button_process_request(cr, uid, ids, context)
        wiz_obj = self.browse(cr, uid, ids, context)[0]
        subsidary_warehouse_dict = {} 
        supply_req_to_wait = []
        supply_req_to_cancel = []
        supply_req_to_confirm = []
        transfer_ids = []
        for wiz_line in wiz_obj.supply_request_line_ids:
            if not wiz_line.qty_to_send:
                continue
            if wiz_line.from_warehouse_id.id not in subsidary_warehouse_dict:
                subsidary_warehouse_dict[wiz_line.from_warehouse_id.id] = [
                    self.trasfer_line_data(cr, uid, ids,wiz_obj,wiz_line,context)]
            else:
                subsidary_warehouse_dict[wiz_line.from_warehouse_id.id].append(
                    self.trasfer_line_data(cr, uid, ids,wiz_obj,wiz_line,context))
            wiz_line.supply_req_id.write({'qty_send':wiz_line.qty_to_send or 0.0})
            supply_req_to_wait.append(wiz_line.supply_req_id.id)
        
        for key in subsidary_warehouse_dict:
            transfer_id = transfer_pool.create(cr, uid, {
                'origin':wiz_line.name,
                'type':'out',
                'date':fields.date.context_today(self,cr,uid,context=context),
                'eta': fields.datetime.now(),
                'company_id': wiz_obj.company_id.id,
                'transfer_id_to_receive':0,
                'warehouse_id':wiz_obj.warehouse_id.id,
                'location_id':wiz_obj.warehouse_id.lot_stock_id.id,
                'warehouse_subsidiary_id':key,
                #'transfer_line':map(lambda x:(0,0,x),subsidary_warehouse_dict[key])
            })
            for transfer_line in subsidary_warehouse_dict[key]:
                supply_req_id = transfer_line['supply_req_id']
                transfer_line.update({'transfer_id': transfer_id, 
                                      'name':request_pool.read(cr, uid, [transfer_line['supply_req_id']], ['name'])[0]['name']})
                transfer_line_id = transfer_line_pool.create(cr, uid, transfer_line)
                request_pool.write(cr, uid, supply_req_id,{'transfer_id': transfer_id,'transfer_line_id':transfer_line_id})
            transfer_ids.append(transfer_id)
        product_purchase_dict = []
        for wiz_line2 in wiz_obj.supply_request_pur_line_ids:
            if wiz_line2.use_old_supply_request:
                new_supply_req_id = wiz_line2.supply_req_id.id
            else:
                new_supply_req_id = request_pool.copy(cr, uid, wiz_line2.supply_req_id.id,{
                    'state':'draft',
                    'qty': wiz_line2.qty_request or 0.0,
                    'qty_send':0.0,
                    'name':'Origin:%s'%wiz_line2.supply_req_id.name,
                    'type':wiz_line2.supply_req_id.type,
                    'from_make_request':True})
            new_supply_req = request_pool.browse(cr, uid, new_supply_req_id)
            if wiz_line2.process_type == 'draft':
                if new_supply_req.type == 'sale' and new_supply_req.state == 'draft':
                    supply_req_to_confirm.append(new_supply_req_id)
                continue
            elif wiz_line2.process_type == 'purchase':
                product_purchase_dict.append({
                        'product_id': wiz_line2.product_id.id,
                        'product_qty': wiz_line2.qty_request,
                        'product_uom': wiz_line2.product_uom_id.id or False,
                        'date_planned': wiz_line2.required_date or False,
                        'origin': wiz_line2.supply_req_id.name,
                    })
                #if wiz_line2.product_id.id not in product_purchase_dict:
                #    product_purchase_dict[wiz_line2.product_id.id] = {
                #        'product_id': wiz_line2.product_id.id,
                #        'product_qty': wiz_line2.qty_request,
                #        'product_uom': wiz_line2.product_uom_id.id or False,
                #        'date_planned': wiz_line2.required_date or False,
                #        'origin': wiz_line2.supply_req_id.name,
                #    }
                #else:
                #    qqty = uom_pool._compute_qty(cr, uid, wiz_line2.product_uom_id.id, 
                #            wiz_line2.qty_request, product_purchase_dict[wiz_line2.product_id.id]['product_uom'])
                #    product_purchase_dict[wiz_line2.product_id.id]['product_qty'] += qqty
                if new_supply_req.type == 'sale' and new_supply_req.state == 'draft':
                    supply_req_to_confirm.append(new_supply_req_id)
            else:
                if new_supply_req.type == 'sale':
                    raise osv.except_osv(_('Error!'), _('You cannot cancel supply request %s of type sale.'%new_supply_req.name))
                supply_req_to_cancel.append(new_supply_req_id)
                continue
            
#                 wf_service.trg_validate(uid, 'stock.supply_request', new_supply_req_id, 'supply_cancel', cr)
        self.create_purchases(cr, uid, ids, wiz_obj,product_purchase_dict, context)
        for req_id in supply_req_to_confirm:
            wf_service.trg_validate(uid, 'stock.supply_request', req_id, 'supply_request_confirm', cr)
        for req_id in supply_req_to_wait:
            wf_service.trg_validate(uid, 'stock.supply_request', req_id, 'supply_transfer_wait', cr)
        for req_id in supply_req_to_cancel:
            wf_service.trg_validate(uid, 'stock.supply_request', req_id, 'supply_cancel', cr)
        return res
    
attend_supply_request()

class attend_request_purchase(osv.osv_memory):
    _name = "attend.request.purchase.line"
    _columns = {
        'wiz_id': fields.many2one('attend.supply.request','Wizard'),
        'supply_req_id': fields.many2one('stock.supply_request','Supply Request'),
        'product_id': fields.many2one('product.product','Product'),
        'name': fields.char('Product Name',size=64,),
        'qty_request': fields.float('Qty Needed',digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom_id':fields.many2one('product.uom','Product UoM'),
        'required_date': fields.datetime('Required Date'),
        'from_warehouse_id': fields.many2one('stock.warehouse_view', 'Required Warehouse'),
        'use_old_supply_request': fields.boolean('Use Old Supply Request'),
        'process_type': fields.selection([('draft','Draft Supply Request'),('purchase','Create Purchase Order'),('cancel','Cancel Supply Request')],'Process Type')
    }
    _defaults = {
        'process_type':'draft'
    }
attend_request_purchase()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
