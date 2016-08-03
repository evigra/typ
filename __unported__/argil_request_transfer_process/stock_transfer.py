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
###############a###############################################################

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp import netsvc

class stock_transfer_line(osv.osv):
    _inherit = "stock.transfer.line"
    _columns = {
        'name' : fields.char('Origin', size=64, readonly=True), 
    }


class stock_transfer(osv.osv):
    _inherit = "stock.transfer"
    _columns = {
    }
    
    
    def action_import_supply_request(self, cr, uid, ids, context=None):
        return True
#         supply_request_pool = self.pool.get('stock.supply_request')
#         transfer_line_pool = self.pool.get('stock.transfer.line')
#         st = self.browse(cr, uid, ids, context=context)[0]
#         supply_request_ids = supply_request_pool.search(cr, SUPERUSER_ID, [
#                                                 ('from_warehouse_id','=',st.warehouse_subsidiary_id.id),
#                                                 ('to_warehouse_id','=',st.warehouse_id.id),
#                                                 ('state','=','confirm'),
#                                                 '|',('transfer_id','=',False),('transfer_id','=',0)])
#         context.update({'active_id': ids and ids[0] or False,
#                         'transfer_company_id':st.company_id.id,
#                         'transfer_warehouse_id': st.warehouse_id.id,
#                         'transfer_supply_request_ids':supply_request_ids,
#                         })
#         if not supply_request_ids:
#             raise osv.except_osv(_('Warning!'), _('There is no draft supply request(s) to import.'))
#         return {
#             'view_type': 'form',
#             'view_mode': 'form',
#             'res_model': 'supply.request.load',
#             'type': 'ir.actions.act_window',
#             'target': 'new',
#             'name': 'Load Supply Request(s)',
#             'context': context
#         }
        
    def action_cancel(self, cr, uid, ids, context=None):
        res = super(stock_transfer, self).action_cancel(cr, uid, ids, context)
        request_ids = self.pool.get('stock.supply_request').search(cr, SUPERUSER_ID, [('transfer_id', 'in', ids)])
        self.pool.get('stock.supply_request').write(cr, SUPERUSER_ID,request_ids,{'transfer_id':0,'qty_send':0.0})
        wf_service = netsvc.LocalService("workflow")
        for req_id in request_ids:
            wf_service.trg_validate(uid, 'stock.supply_request', req_id, 'stock_transfer_confirm', cr)
        return res
    
    def get_receive_line_data(self, cr, uid, transfer, line, context=None):
        result = super(stock_transfer, self).get_receive_line_data(cr, uid,transfer, line, context)
        print "line.name: ", line.name
        print "line.product_id (%s) %s" % (line.product_id.id, line.product_id.name)
        print "line.qty: ", line.qty
        result.update({'dest_move_id':line.dest_move_id,
                       'supply_req_id':line.supply_req_id,
                       'name' : line.name})
        print "result: ", result
        return result
    
    def create_transfer_to_receive(self, cr, uid, transfer, context=None):
        result = super(stock_transfer, self).create_transfer_to_receive(cr, uid,transfer, context)
        wf_service = netsvc.LocalService("workflow")
        for line in transfer.transfer_line:
            if line.supply_req_id:
                wf_service.trg_validate(uid, 'stock.supply_request', line.supply_req_id, 'supply_ready_receive', cr)
        return result
    
#     def action_confirm_transfer(self, cr, uid, ids, context=None):
#         result = super(stock_transfer, self).action_confirm_transfer(cr, uid,ids, context)
#         for rec in self.browse(cr, uid, ids, context=context):
#             transfer_type = rec.type
#             if transfer_type == 'in':
#                 for line 
#         return result
    


class stock_transfer_line(osv.osv):
    _inherit = "stock.transfer.line"
    _columns = {
        'supply_req_id': fields.integer('Supply Request'),
        'dest_move_id': fields.integer('Related Move ID',help="For internal use. This id is linked to the receiving stock move"),
        
    }
    
    def create_stock_move(self, cr, uid, line, stock_move_obj, transfer_type, location_id, company_id, context=None):
        result = super(stock_transfer_line, self).create_stock_move(cr, uid, line, stock_move_obj, transfer_type, location_id, company_id, context)
        if not line:
            return result
        if context is None:
            context = {} 
        if transfer_type == 'in':
            result.update({
                'move_dest_id': line.dest_move_id or False,
            })
        return result
    
    def action_confirm(self, cr, uid, ids, transfer_type, location_id, context=None):
        if context is None:
            context = {}
        supply_request_pool = self.pool.get('stock.supply_request') 
        result = super(stock_transfer_line, self).action_confirm(cr, uid, ids, transfer_type,location_id,context=context)
        for line in self.browse(cr, uid, ids):
            if transfer_type == 'in' and line.supply_req_id:
                supply_request_obj = supply_request_pool.browse(cr, uid, line.supply_req_id)
#                 flag = False
#                 request_update_data = {'qty_send':line.qty + supply_request_obj.qty}
#                 if not round(supply_request_obj.qty - (line.qty + supply_request_obj.qty)):
#                     flag = True
#                 supply_request_pool.write(cr, uid,line.supply_req_id,request_update_data )
#                 if flag:
                supply_request_pool.done_supply_request(cr, uid, [line.supply_req_id], context)
#             elif transfer_type == 'out' and line.supply_req_id:
#                 supply_request_pool.action_confirm_request(cr, SUPERUSER_ID, [line.supply_req_id], context)
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
