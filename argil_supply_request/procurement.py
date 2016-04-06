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

from openerp.osv import osv, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import netsvc
from openerp import pooler
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp import tools

class procurement_order(osv.osv):
    _inherit = "procurement.order"
    _columns = {
        'procure_method': fields.selection([('make_to_stock','Make to Stock'),
                                            ('make_to_order','Make to Order'),
                                            ('make_to_supply_request','Make to Supply Request')], 
                                           'Procurement Method', readonly=True, required=True,
                                           states={'draft':[('readonly',False)], 'confirmed':[('readonly',False)]}, 
                                           help="If you encode manually a Procurement, you probably want to use" \
                                           " a make to order method."),
        'supply_req_id': fields.many2one('stock.supply_request','Supply Request'),
        'distribution_type':fields.selection([('manual', 'Manual'), ('stock_reorder','Stock Re-order'), ('sale', 'Sale')], 'Distribution Type'),
    }
    
    _defaults = {
        'distribution_type':'manual'
    }
    def _check_make_to_supply_request_service(self, cr, uid, procurement, context=None):
        """
           This method may be overrided by objects that override procurement.order
           for computing their own purpose
        @return: True"""
        return True
    
    def check_make_supply_request(self, cr, uid, ids, context=None):
        ''' return True if supply request is needed
        '''
        ok = True
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_id.type == 'service':
                ok = ok and self._check_make_to_supply_request_service(cr, uid, procurement, context)
            else:
                ok = ok and self._check_make_to_supply_request_product(cr, uid, procurement, context)
        return ok
    
    
    def check_make_supply_request_done(self, cr, uid, ids, context=None):
        ok = True
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.supply_req_id and procurement.supply_req_id.state != 'done':
                return False
        return True
    
    def action_supply_req_assign(self, cr, uid, ids, context=None):
        """ This is action which call from workflow to assign purchase requisition to procurements
        @return: True
        """
        res = self.make_supply_request_sale(cr, uid, ids, context=context)
        res = res.values()
        return len(res) and res[0] or 0 #TO CHECK: why workflow is generated error if return not integer value
 
    def action_supply_move_assigned(self, cr, uid, ids, context=None):
        """ Changes procurement state to Running and writes message.
        @return: True
        """
        message = _('Supply Request created.')
        self.write(cr, uid, ids, {'state': 'running',
                'message': message}, context=context)
        self.message_post(cr, uid, ids, body=message, context=context)
        return True
    
    def get_supply_request_data(self,cr, uid, order_point, qty,type='manual',
                                move_obj=False,procurement=False, context=None):
#         self.pool.get('stock.warehouse')
        partner_id = False
        if move_obj:
            if move_obj.sale_line_id:
                partner_id = move_obj.sale_line_id.address_allotment_id and move_obj.sale_line_id.address_allotment_id.id or False
                if not partner_id:
                    partner_id = move_obj.sale_line_id.order_id.partner_id.id or False
        if not partner_id:
            partner_id = order_point.warehouse_id.partner_id and order_point.warehouse_id.partner_id.id or False
        
        return {
                'name': procurement and procurement.origin +':'+ order_point.name or order_point.name ,
                'product_id': procurement and procurement.product_id.id or order_point.product_id.id or False,
                'qty': qty,
                'partner_address_destination': partner_id,
                'product_uom_id':procurement and procurement.product_uom.id or order_point.product_uom.id or False,
                'date': move_obj and move_obj.create_date or self._get_orderpoint_date_planned(cr, uid, order_point, datetime.today(),context=context),
                'required_date':move_obj and move_obj.date_expected or self._get_orderpoint_date_planned(cr, uid, order_point, datetime.today(),context=context),
                'to_warehouse_id': order_point.dist_center_warehouse_id.id or False,
#                 'to_location_id':order_point.location_id.id or False,
#                 'to_company_id':order_point.company_id.id or False,
                'from_warehouse_id':order_point.warehouse_id.id or False,
#                 'from_location_id':order_point.location_id.id or False,
#                 'from_company_id': order_point.company_id.id or False,
                'state':'draft',
                'type':type,
                'dest_move_id': move_obj and move_obj.id or False,
            }
    
    def get_supply_request_data_wo_orderpoint(self,cr, uid, qty,type='manual',
                                move_obj=False,procurement=False, context=None):
#         self.pool.get('stock.warehouse')
        partner_id = False
        warehouse_id, distribution_warehouse_id = False, False
        
        if procurement:
            warehouse_id, distribution_warehouse_id = self.get_distribution_warehouse(cr, uid, procurement,context)
            warehouse_obj = self.pool.get('stock.warehouse').browse(cr, uid, warehouse_id, context)
        if move_obj:
            if move_obj.sale_line_id:
                partner_id = move_obj.sale_line_id.address_allotment_id and move_obj.sale_line_id.address_allotment_id.id or False
                if not partner_id:
                    partner_id = move_obj.sale_line_id.order_id.partner_id.id or False
        if not partner_id:
            partner_id = warehouse_obj.partner_id and warehouse_obj.partner_id.id or False
        
        return {
                'name': procurement and procurement.origin,
                'product_id': procurement and procurement.product_id.id or False,
                'qty': qty,
                'partner_address_destination': partner_id,
                'product_uom_id':procurement and procurement.product_uom.id or False,
                'date': move_obj and move_obj.create_date or datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'required_date': move_obj and move_obj.date_expected or datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
                'to_warehouse_id': distribution_warehouse_id or False,
#                 'to_location_id':order_point.location_id.id or False,
#                 'to_company_id':order_point.company_id.id or False,
                'from_warehouse_id':warehouse_id or False,
#                 'from_location_id':order_point.location_id.id or False,
#                 'from_company_id': order_point.company_id.id or False,
                'state':'draft',
                'type':type,
                'dest_move_id':move_obj and move_obj.id or False,
            }
    def get_supply_request_move_data(self,cr, uid, order_point,qty, context=None):
        return {
            'name': order_point.name,
            'location_id': order_point.product_id.property_stock_procurement.id or False,
            'location_dest_id': order_point.location_id.id or False,
            'product_id': order_point.product_id.id,
            'product_qty': qty,
            'product_uom': order_point.product_uom.id,
            'date_expected': order_point.required_date or order_point.date or False,
            'state': 'draft',
            'company_id': order_point.company_id.id or False,
            'auto_validate': True,
        }
        
    def make_supply_request_sale(self,cr, uid, ids, context=None):
        res = {}
        if context is None:
            context = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
        supply_request_pool = self.pool.get('stock.supply_request')
        location_pool = self.pool.get('stock.location')
        orderpoint_pool = self.pool.get('stock.warehouse.orderpoint')
        stock_move_pool = self.pool.get('stock.move')
        uom_pool = self.pool.get('product.uom')
        wf_service = netsvc.LocalService("workflow")
        for procurement in self.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            uom_id = procurement.product_id.uom_po_id.id
            qty = uom_pool._compute_qty(cr, uid, procurement.product_uom.id, procurement.product_qty, procurement.product_uom.id) #uom_id)
            supply_request_type = procurement.distribution_type or 'sale'
            order_point_ids = orderpoint_pool.search(cr, uid, [('product_id', '=', procurement.product_id.id),
                                                              ('location_id', '=', procurement.location_id.id),
                                                              ('supply_from_dist_center', '=', True)], 
                                                    context=context)
            if order_point_ids:
                order_point = orderpoint_pool.browse(cr,uid, order_point_ids)[0]
                supply_request_data = self.get_supply_request_data(cr, uid,order_point,\
                                        qty,supply_request_type,procurement.move_id or False,
                                        procurement, context)
            else:
                supply_request_data = self.get_supply_request_data_wo_orderpoint(cr, uid,
                                        qty,supply_request_type,procurement.move_id or False,
                                        procurement, context)
            supply_req_id = supply_request_pool.create(cr, uid, supply_request_data)
            res[procurement.id] = supply_req_id
#                 move_data = self.get_supply_request_move_data(cr, uid, order_point,qty, context)
#                 move_id = stock_move_pool.create(cr, uid, move_data)
#                 stock_move_pool.action_confirm(cr, uid, [move_id], context=context)
#                 supply_request_pool.write(cr, uid, supply_req_id, {'dest_move_id':res_id})
            self.write(cr, uid, [procurement.id], {'state': 'running', 'supply_req_id': res[procurement.id]})
            wf_service.trg_validate(uid, 'stock.supply_request', supply_req_id, 'supply_request_confirm', cr)
        return res
    
    def _prepare_orderpoint_procurement(self, cr, uid, orderpoint, product_qty, context=None):
        result = super(procurement_order, self)._prepare_orderpoint_procurement(cr, uid, orderpoint, product_qty, context=context)
        result.update({'distribution_type': context.get('automatic_supply_request', False) \
                       and 'stock_reorder' or 'manual',
                       'procure_method': context.get('automatic_supply_request', False) and \
                       'make_to_supply_request' or 'make_to_order',})
        return result
    
    def make_automatic_supply_request(self, cr, uid, order_point, context=None):
        res = {}
        supply_req_id = False
        if context is None: context= {}
        wf_service = netsvc.LocalService("workflow")
        supply_request_pool = self.pool.get('stock.supply_request')
        procurement_pool = self.pool.get('procurement.order')
        stock_move_pool = self.pool.get('stock.move')
        location_pool = self.pool.get('stock.location')
        orderpoint_pool = self.pool.get('stock.warehouse.orderpoint')
        prods = location_pool._product_virtual_get(cr, uid,
                order_point.location_id.id, [order_point.product_id.id],
                {'uom': order_point.product_uom.id})[order_point.product_id.id]
        if prods < order_point.product_min_qty:
            qty = max(order_point.product_min_qty, order_point.product_max_qty)-prods

            reste = qty % order_point.qty_multiple
            if reste > 0:
                qty += order_point.qty_multiple - reste

            if qty <= 0:
                return True
            if order_point.product_id.type not in ('consu'):
                if order_point.procurement_draft_supply_ids:
                # Check draft procurement related to this order point
                    pro_ids = [x.id for x in order_point.procurement_draft_supply_ids]
                    procure_datas = procurement_pool.read(
                        cr, uid, pro_ids, ['id', 'product_qty'], context=context)
                    to_generate = qty
                    for proc_data in procure_datas:
                        if to_generate >= proc_data['product_qty']:
                            wf_service.trg_validate(uid, 'procurement.order', proc_data['id'], 'button_confirm', cr)
                            procurement_pool.write(cr, uid, [proc_data['id']],  {'origin': order_point.name}, context=context)
                            to_generate -= proc_data['product_qty']
                        if not to_generate:
                            break
                    qty = to_generate
            if qty > 0:
                context.update({'automatic_supply_request':True})
                proc_id = procurement_pool.create(cr, uid,
                                self._prepare_orderpoint_procurement(cr, uid, order_point, qty, context=context),
                                                context=context)
                wf_service.trg_validate(uid, 'procurement.order', proc_id,
                        'button_confirm', cr)
                wf_service.trg_validate(uid, 'procurement.order', proc_id,
                        'button_check', cr)
                orderpoint_pool.write(cr, uid, [order_point.id],
                        {'procurement_id': proc_id}, context=context)
#             supply_request_type = 'stock_reorder'
#             supply_request_data = self.get_supply_request_data(cr, uid, order_point,\
#                                                                qty,supply_request_type, context)
#             supply_id = supply_request_pool.create(cr, uid, supply_request_data)
#             move_data = get_supply_request_move_data(cr, uid, order_point,qty, context)
#             move_id = stock_move_pool.create(cr, uid, move_data)
#             stock_move_pool.action_confirm(cr, uid, [move_id], context=context)
#             supply_request_pool.write(cr, uid,supply_id, {'dest_move_id':move_id})
#             
#             self.write(cr, uid, [procurement_id], { 'supply_id': supply_id})
        return True
    
    def update_supply_request(self, cr, uid, order_point, context=None):
        #TODO
        return True
    
    def get_distribution_warehouse(self, cr, uid, procurement, context=None):
        location_pool = self.pool.get('stock.location')
        warehouse_pool = self.pool.get('stock.warehouse')
        warehouse_id,dist_warehouse_id = False,False
        all_warehouse_ids = warehouse_pool.search(cr, uid, [('company_id','=',procurement.company_id.id)])
        for warehouse in warehouse_pool.read(cr, uid, all_warehouse_ids, ['lot_stock_id','lot_input_id','dist_center_warehouse_id']):
            if procurement.location_id.id in [warehouse['lot_stock_id'][0],warehouse['lot_input_id'][0]]:
                warehouse_id, dist_warehouse_id = warehouse['id'],warehouse['dist_center_warehouse_id'] and warehouse['dist_center_warehouse_id'][0] or False
                break
        return warehouse_id,dist_warehouse_id
        
    def _check_make_to_supply_request_product(self, cr, uid, procurement, context=None):
        """ Checks procurement move state.
        @param procurement: Current procurement.
        @return: True or move id.
        """
        ok = True
        if context is None: context = {}
        if procurement.move_id:
            message = False
            move_id = procurement.move_id.id
            if not (procurement.move_id.state in ('done','assigned','cancel')):
                ok = ok and self.pool.get('stock.move').action_assign(cr, uid, [move_id])
                cntxt = context.copy()
#                 cntxt.update({'search_all_op':True})
                order_point_id = self.pool.get('stock.warehouse.orderpoint').search(cr, uid, [('product_id', '=', procurement.product_id.id),
                                                                                              ('location_id', '=', procurement.location_id.id),
                                                                                              ('supply_from_dist_center', '=', True)], 
                                                                                    context=cntxt)
#                 if not order_point_id and procurement.distribution_type == 'sale'
                if not order_point_id:
                    if procurement.distribution_type == 'sale' and \
                                self.get_distribution_warehouse(cr, uid, procurement,context)[1]:
                        message = _("Procurement '%s' is running: ") % (procurement.name) + "Supply Request Created"
                        ctx_wkf = dict(context or {})
                        ctx_wkf['workflow.trg_write.%s' % self._name] = False
                        self.write(cr, uid, [procurement.id], {'message': message},context=ctx_wkf)
                        return True
                    else:
                        message = _("No minimum orderpoint rule defined and no distribution center specified in warehouse")
                        ctx_wkf = dict(context or {})
                        ctx_wkf['workflow.trg_write.%s' % self._name] = False
                        self.write(cr, uid, [procurement.id], {'message': message},context=ctx_wkf)
                        return ok
                elif not ok:
                    message = _("Not enough stock. Waiting for Supply Request")
 
                if message:
                    message = _("Procurement '%s' is running: ") % (procurement.name) + message
                    #temporary context passed in write to prevent an infinite loop
                    ctx_wkf = dict(context or {})
                    ctx_wkf['workflow.trg_write.%s' % self._name] = False
                    self.write(cr, uid, [procurement.id], {'message': message},context=ctx_wkf)
        return True
        
    def _product_virtual_get(self, cr, uid, order_point):
        #TODO
        
        if not order_point.supply_from_dist_center:
            return super(procurement_order, self)._product_virtual_get(cr, uid, order_point)
        if order_point.supply_req_ids:
            self.update_supply_request(cr, uid,order_point)
            return None
        else:
            self.make_automatic_supply_request(cr, uid, order_point)
            return None
#         if procurement and procurement.state != 'exception' and procurement.purchase_id and procurement.purchase_id.state in ('draft', 'confirmed'):
#             return None
        return super(procurement_order, self)._product_virtual_get(cr, uid, order_point)

    def _procure_confirm(self, cr, uid, ids=None, use_new_cursor=False, context=None):
        '''
        Call the scheduler to check the procurement order

        @param self: The object pointer
        @param cr: The current row, from the database cursor,
        @param uid: The current user ID for security checks
        @param ids: List of selected IDs
        @param use_new_cursor: False or the dbname
        @param context: A standard dictionary for contextual values
        @return:  Dictionary of values
        '''
        res = super(procurement_order, self)._procure_confirm(cr, uid, ids=ids, use_new_cursor=use_new_cursor, context=context)
        if context is None:
            context = {}
        try:
            if use_new_cursor:
                cr = pooler.get_db(use_new_cursor).cursor()
            wf_service = netsvc.LocalService("workflow")

            procurement_obj = self.pool.get('procurement.order')
            if not ids:
                ids = procurement_obj.search(cr, uid, [('state', '=', 'exception')], order="date_planned")
            for id in ids:
                wf_service.trg_validate(uid, 'procurement.order', id, 'button_restart', cr)
            if use_new_cursor:
                cr.commit()
            company = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id
            maxdate = (datetime.today() + relativedelta(days=company.schedule_range)).strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
            start_date = fields.datetime.now()
            offset = 0
            report = []
            report_total = 0
            report_except = 0
            report_later = 0

            while True:
                report_ids = []
                ids = procurement_obj.search(cr, uid, [('state', '=', 'confirmed'), ('procure_method', '=', 'make_to_supply_request')], offset=offset)
                for proc in procurement_obj.browse(cr, uid, ids):
                    if maxdate >= proc.date_planned:
                        wf_service.trg_validate(uid, 'procurement.order', proc.id, 'button_check', cr)
                        report_ids.append(proc.id)
                    else:
                        report_later += 1
                    report_total += 1

                    if proc.state == 'exception':
                        report.append(_('PROC %d: from supply request - %3.2f %-5s - %s') % \
                                (proc.id, proc.product_qty, proc.product_uom.name,
                                    proc.product_id.name,))
                        report_except += 1


                if use_new_cursor:
                    cr.commit()
                offset += len(ids)
                if not ids: break
            end_date = fields.datetime.now()

            if use_new_cursor:
                cr.commit()
        finally:
            if use_new_cursor:
                try:
                    cr.close()
                except Exception:
                    pass
        return res
procurement_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
