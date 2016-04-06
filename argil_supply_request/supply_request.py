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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import netsvc
from openerp import SUPERUSER_ID

class stock_supply_request(osv.osv):
    _name = 'stock.supply_request'     
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    def _get_residual(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = 0
            residue = obj.qty - obj.qty_send
            res[obj.id] = residue
        return res
    
    def _get_complaince(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        residue = 0
        for obj in self.browse(cr, uid, ids, context=context):
            residue = 0.0
            res[obj.id] = 0.0
            if obj.qty_send and obj.qty:
                residue = (obj.qty_send / obj.qty)*100
            res[obj.id] = residue
        return res
    
    def _get_uom_id(self, cr, uid, context=None):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False
        
    _columns = {
        'name': fields.char('Origin',size=64,required=True),
        'product_id': fields.many2one('product.product', 'Product',required=True, help='Stockable Products'),
        'qty': fields.float('Qty Requested'),
        'qty_send': fields.float('Qty Send'),
        'residual': fields.function(_get_residual, type='float', string='Residual'),
        'compliance': fields.function(_get_complaince, type='float', string='Percentage Compliance'),
        'product_uom_id': fields.many2one('product.uom', 'Product UOM'),
        'date': fields.datetime('Date'),
        'required_date': fields.datetime('Required Date'),
        'to_warehouse_id': fields.many2one('stock.warehouse_view', 'To Warehouse',help="To which warehouse the request is send"),
#         'to_location_id': fields.many2one('stock.location', 'To Stock Location'),
#         'to_company_id': fields.many2one('res.company', 'To Company'),
        'from_warehouse_id': fields.many2one('stock.warehouse_view', 'From Warehouse',help="From which warehouse the request is generated"),
#         'from_location_id': fields.many2one('stock.location', 'From Stock Location'),
#         'from_company_id': fields.many2one('res.company', 'From Company'),
        #         'transfer_id': fields.many2one('stock.transfer', 'Stock Product Transfer'),
        'state': fields.selection([('draft', 'Draft'), ('confirm','Confirmed'), 
                                   ('done', 'Done'), ('cancel','Cancel')], 'State'),
        'partner_address_destination':fields.many2one('res.partner', 'Partner Address Destination'),
        'type': fields.selection([('manual', 'Manual'), ('stock_reorder','Stock Re-order'), 
                                  ('sale', 'Sale')], 'Type'),
#         'supply_req_id': fields.integer('Origin Supply request ID',),
        'dest_move_id': fields.many2one('stock.move','Stock Move',ondelete='set null'),
        'from_make_request': fields.boolean('From Make Request'),
        'attend_request':fields.boolean('Attend Request'),
        'product_name': fields.related('product_id','default_code',size=64,type='char',
                                       string='Product Name',store=True)
    }
    _defaults = {
        'from_make_request':True,
        'type':'manual',
        'state':'draft',
        'product_uom_id': _get_uom_id,
        'date':fields.datetime.now
    }
    
    def copy(self, cr, uid, id, default=None, context=None):
        if default is None: default={}
        if 'type' not in default:
            default.update({'type':'manual'})
        default.update({'attend_request':False,
#                         'type':'manual',
                        'state':'draft','qty_send':0.0})
        return super(stock_supply_request, self).copy(cr, uid, id, default, context=context)

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        result = {'value':{}}
        if context is None:
            context = {}
        product_product = self.pool.get('product.product')
        if not product_id: return result
#         context_partner = context.copy()
# #         if partner_id:
#             lang = res_partner.browse(cr, uid, partner_id).lang
#             context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context)
        result['domain'] = {'product_uom': [('category_id','=',product.uom_id.category_id.id)]}
        result['value'].update({'product_uom': product.uom_id.id})
        return result
    
    def cancel_supply_request(self, cr, uid, ids, context=None):
#         res = super(stock_supply_request, self).tender_cancel(cr, uid, ids, context=context)
        #for req in self.browse(cr, uid, ids, context=context):
        #    if req.type == 'sale':
        #        raise osv.except_osv(_('Error!'), _('You cannot cancel a request created from sale order'))
        self.write(cr, uid, ids,{'state':'cancel'}, context)
        wf_service = netsvc.LocalService("workflow")
        for req_id in ids:
            wf_service.trg_validate(uid, 'stock.supply_request', req_id, 'supply_cancel', cr)
        return True
    
    def action_confirm_request(self, cr, uid, ids, context=None):
        
        wf_service = netsvc.LocalService("workflow")
        for req_id in ids:
            wf_service.trg_validate(uid, 'stock.supply_request', req_id, 'supply_request_confirm', cr)
        return True
    
    def check_confirm_request(self, cr, uid, ids, context=None):
        #For injecting atend supply request
        self.write(cr, uid, ids,{'state':'confirm',
                                 'attend_request':True,
                                 }, context=context)
        return True
    
    def done_supply_request(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids,{'state':'done'}, context)
        wf_service = netsvc.LocalService("workflow")
        for req_id in ids:
            wf_service.trg_validate(uid, 'stock.supply_request', req_id, 'supply_request_done', cr)
        return True
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None: context = {}
        result = super(stock_supply_request, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if context.get('from_make_supply',False) and result.get('toolbar', False) and result['toolbar'].get('action',False):
            temps = result['toolbar']['action']
            for i,action in enumerate(temps):
                if action.get('res_model',False) ==  'attend.supply.request':
                    del result['toolbar']['action'][i]
        return result
    
stock_supply_request()

class stock_warehouse_orderpoint(osv.osv):
    _inherit = "stock.warehouse.orderpoint"
    
    def _get_draft_supply_procurements(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        procurement_obj = self.pool.get('procurement.order')
        for orderpoint in self.browse(cr, uid, ids, context=context):
            procurement_ids = procurement_obj.search(cr, uid , [
                                            ('state', 'in', ['draft','running']),
                                            ('procure_method','=','make_to_supply_request'),
                                            ('product_id', '=', orderpoint.product_id.id),
                                            ('location_id', '=', orderpoint.location_id.id)])
            result[orderpoint.id] = procurement_ids
        return result
    
    def _get_draft_supply_request(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        supply_pool = self.pool.get('stock.supply_request')
        for orderpoint in self.browse(cr, uid, ids, context=context):
            supply_req_ids = supply_pool.search(cr, uid , [
                               ('state', '=', 'draft'), 
                               ('product_id', '=', orderpoint.product_id.id), 
                               ('from_warehouse_id', '=', orderpoint.warehouse_id.id),
                               ('to_warehouse_id','=',orderpoint.dist_center_warehouse_id.id)])
            result[orderpoint.id] = supply_req_ids
        return result
    
    _columns = {
        'supply_from_dist_center': fields.boolean('Supply From Distribution Center'),
        'dist_company_id': fields.many2one('res.company','Distribution Company'),
        'dist_center_warehouse_id': fields.many2one('stock.warehouse_view', 'Distribution Center Warehouse'),
#         'dist_center_location_id': fields.many2one('stock.location','Distribution Center Location'),
        'supply_req_ids': fields.function(_get_draft_supply_request, type='many2many', 
                        relation="stock.supply_request", string="Related Supply Requests",
                        help="Draft supply request of the product and location of that orderpoint"),
        'procurement_draft_supply_ids': fields.function(_get_draft_supply_procurements, 
                                type='many2many', relation="procurement.order", \
                                string="Related Supply Procurement Orders",
                                help="Draft procurement of the product and location of that orderpoint"),
    }

stock_warehouse_orderpoint()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
