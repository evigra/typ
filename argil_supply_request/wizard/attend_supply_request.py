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
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class attend_supply_request(osv.osv_memory):
    _name = "attend.supply.request"
    _columns = {
        'supply_request_line_ids': fields.one2many('attend.supply.request.line','wiz_id','Supply Request'),
        'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
        'company_id': fields.many2one('res.company','Company'),
        'state': fields.selection([('phase1','Phase 1'),('phase2','Phase 2'),('phase3','Phase 3')],'State'),
    }
    _defaults = {
        'state':'phase1',
        'company_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    
    }
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(attend_supply_request, self).default_get(cr, uid, fields, context=context)
        active_ids = context.get('active_ids')
        warehouse_ids = self.get_warehouse_id(cr, uid, active_ids, context)
        if len(warehouse_ids) > 1:
            raise osv.except_osv(_('Error!'), _('Please choose supply request(s) to any one warehouse.'))
        warehouse_id = warehouse_ids[0]
        supply_request_line_ids = self._partial_supply_request_for(cr, uid, active_ids,warehouse_id, context)
        res.update(warehouse_id=warehouse_id,supply_request_line_ids=supply_request_line_ids)
        return res
    
    def get_warehouse_id(self, cr, uid, supply_request_ids, context=None):
        supply_request_pool = self.pool.get('stock.supply_request')
        warehouse_dict = {}
        for supply_request in supply_request_pool.browse(cr, uid, supply_request_ids):
            warehouse_dict.update({supply_request.to_warehouse_id.id:True})
        return warehouse_dict.keys()
        
    def get_missing_product_qty(self, cr, uid, product_data,product_obj, warehouse_id,to_uom_id, context=None):
        """Its for considering any other product qty and uom. Usable in stock transfer"""
        uom_pool = self.pool.get('product.uom')
        product_data['v_avail'] = uom_pool._compute_qty(cr, uid, product_obj.uom_id.id, product_data['v_avail'], to_uom_id)
        return product_data
    
    def _partial_supply_request_for(self, cr, uid, supply_request_ids, warehouse_id,context=None):
        result = []
        supply_request_pool = self.pool.get('stock.supply_request')
        product_pool = self.pool.get('product.product')
        product_dict = {}
        supply_request_ids = supply_request_pool.search(cr, uid, [('id','in',supply_request_ids),
                                                                  ('state','=','confirm')],order='product_name,required_date')
        count = 0
        for supply_request in supply_request_pool.browse(cr, uid, supply_request_ids):
            product_id = supply_request.product_id.id or False
            if product_id not in product_dict:
                prdt_cntxt = context.copy()
                prdt_cntxt.update({'warehouse':warehouse_id,})#'uom':supply_request.product_uom_id.id
                product = product_pool.browse(cr, uid, supply_request.product_id.id,context=prdt_cntxt)
                product_dict[product_id] = {'s_avail': product.qty_available,
                                            'v_avail':product.qty_available
                                            }
                product_dict[product_id] = self.get_missing_product_qty(cr, uid, 
                                            product_dict[product_id],product,warehouse_id,supply_request.product_uom_id.id,context)
            data_dict = {
                'sequence_no':count,
                'supply_req_id': supply_request.id,
                'name': supply_request.product_id.default_code or '',
                'product_id': product_id or False,
                'required_date': supply_request.required_date or False,
                'qty_request':supply_request.qty,
                'qty_available':product_dict[product_id]['v_avail'],
                'product_uom_id':supply_request.product_uom_id.id or False,
                'from_warehouse_id': supply_request.from_warehouse_id.id or False,
                }#'qty_to_send'
            if supply_request.qty >= product_dict[product_id]['v_avail']:
                data_dict.update({
                    'qty_to_send':product_dict[product_id]['v_avail']
                })
                product_dict[product_id]['v_avail'] = 0.0
            elif supply_request.qty < product_dict[product_id]['v_avail']:
                data_dict.update({
                    'qty_to_send': supply_request.qty
                })
                product_dict[product_id]['v_avail'] = product_dict[product_id]['v_avail'] - \
                                                            supply_request.qty
                
#             result.append()
            result.append(data_dict)
            count+=1
        return result
    
    def button_update_lines(self, cr, uid, ids, context=None):
        self.update_lines(cr, uid,ids, context)
        return {
              'name': _('Attend Supply Request'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'attend.supply.request',
              'type': 'ir.actions.act_window',
              'res_id': ids and ids[0] or False,
              'target':'new'
              }
    
    def update_lines(self, cr, uid, ids, context=None):
        wiz_obj = self.browse(cr, uid, ids, context)[0]
        product_pool = self.pool.get('product.product')
        product_dict = {} 
        for wiz_line in wiz_obj.supply_request_line_ids:
            if wiz_line.product_id.id not in product_dict:
                prdt_cntxt = context.copy()
                prdt_cntxt.update({'warehouse':wiz_obj.warehouse_id.id,'uom':wiz_line.product_uom_id.id})
                product = product_pool.browse(cr, uid, wiz_line.product_id.id,context=prdt_cntxt)
                wiz_line.write({'qty_available':product.virtual_available})
                product_dict[wiz_line.product_id.id] = product.virtual_available - wiz_line.qty_to_send
            else:
                wiz_line.write({'qty_available':product_dict[wiz_line.product_id.id]})
                if wiz_line.qty_to_send > product_dict[wiz_line.product_id.id]:
                    wiz_line.write({'need_check':True})
                    wiz_obj.write({'state':'phase1'})
                else:
                    product_dict[wiz_line.product_id.id] -= wiz_line.qty_to_send
                    
        return True
    
    def button_goto_phase1(self,cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'phase1'})
        return {
              'name': _('Attend Supply Request'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'attend.supply.request',
              'type': 'ir.actions.act_window',
              'res_id': ids and ids[0] or False,
              'target':'new'
              }
    
    def button_goto_phase2(self,cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'phase2'})
        self.update_lines(cr, uid,ids, context)
        return {
              'name': _('Attend Supply Request'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'attend.supply.request',
              'type': 'ir.actions.act_window',
              'res_id': ids and ids[0] or False,
              'target':'new'
              }
      
    def button_process_request(self, cr, uid, ids, context=None):
        #code injector function
        return True
#         {
#               'name': _('Attending Supply Request(s)'),
#               'view_type': 'form',
#               "view_mode": 'tree,form',
#               'res_model': 'stock.supply_request',
#               'type': 'ir.actions.act_window',
#               }
    
    
attend_supply_request()

class attend_supply_request_line(osv.osv_memory):
    _name = 'attend.supply.request.line'
    _columns = {
        'wiz_id': fields.many2one('attend.supply.request','Wizard'),
        'supply_req_id': fields.many2one('stock.supply_request','Supply Request'),
        'product_id': fields.many2one('product.product','Product'),
        'name': fields.char('Product Name',size=64,),
        'qty_request': fields.float('Qty Requested',digits_compute=dp.get_precision('Product Unit of Measure')),
        'qty_available': fields.float('Qty Available',digits_compute=dp.get_precision('Product Unit of Measure'),help="Its the forecast qty after every other allocation"),
        'qty_to_send': fields.float('Qty to Send',digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom_id':fields.many2one('product.uom','Product UoM'),
        'required_date': fields.datetime('Required Date'),
        'need_check': fields.boolean('Need to check'),
        'from_warehouse_id': fields.many2one('stock.warehouse_view', 'Required Warehouse'),
        'sequence_no': fields.integer('Sequence'),
    }
    _order = "sequence_no"
    _defaults = {
        'qty_to_send':0.0
    }
    def onchange_qty(self, cr, uid, ids, qty, qty_request, qty_available, product_id, context=None):
        result = {'value':{'need_check':False}}
        """if qty > qty_request:
            result['warning'] ={
                       'title': _('Check Qty!'),
                       'message' : _('Qty entered is greater than requested')
                    }
            result['value'].update({'qty_to_send':0.0,'need_check':True}) """
        if qty > qty_available:
            result['warning'] ={
                       'title': _('Check Qty!'),
                       'message' : _('Qty entered is greater than available')
                    }
            result['value'].update({'qty_to_send':0.0,'need_check':True})
        return result
    
attend_supply_request_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
