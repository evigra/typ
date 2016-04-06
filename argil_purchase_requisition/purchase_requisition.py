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

from openerp import netsvc

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"

    def tender_cancel(self, cr, uid, ids, context=None):
        res = super(purchase_requisition, self).tender_cancel(cr, uid, ids, context=context)
        wf_service = netsvc.LocalService("workflow")
        for pr_id in ids:
            wf_service.trg_validate(uid, 'purchase.requisition', pr_id, 'requisition_cancel', cr)
        return res
    
    def tender_reset(self, cr, uid, ids, context=None):
        res = super(purchase_requisition, self).tender_reset(cr, uid, ids, context=None)
        wf_service = netsvc.LocalService("workflow")
        for pr_id in ids:
            wf_service.trg_delete(uid, 'purchase.requisition', pr_id, cr)
            wf_service.trg_create(uid, 'purchase.requisition', pr_id, cr)
        return res

    def tender_done(self, cr, uid, ids, context=None):
        res = super(purchase_requisition, self).tender_done(cr, uid, ids, context=context)
        wf_service = netsvc.LocalService("workflow")
        for pr_id in ids:
            wf_service.trg_validate(uid, 'purchase.requisition', pr_id, 'requisition_done', cr)
        return res
    
    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """
        Create New RFQ for Supplier
        """
        if context is None:
            context = {}
        assert partner_id, 'Supplier should be specified'
        purchase_order_pool = self.pool.get('purchase.order')
        purchase_order_line_pool = self.pool.get('purchase.order.line')
        res = super(purchase_requisition, self).make_purchase_order(cr, uid, ids, partner_id, context=context)
        ####TODO
        proc_move_dict = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            purchase_id = res[requisition.id]
            for line in requisition.line_ids:
                if not line.proc_move_id or not line.product_id:
                    continue
                if line.proc_move_id.id not in proc_move_dict:
                    proc_move_dict[line.product_id.id] = line.proc_move_id.id or False
            purchase_obj = purchase_order_pool.browse(cr, uid, purchase_id)
            for purchase_line in purchase_obj.order_line:
                if purchase_line.product_id and purchase_line.product_id.id in proc_move_dict:
                    purchase_order_line_pool.write(cr, uid,[purchase_line.id],{'move_dest_id':proc_move_dict[purchase_line.product_id.id]} )
        return res
        
    def action_requisition_done(self, cr, uid, ids, context=None):
        return True
     
purchase_requisition()

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"
    _columns = {
        'proc_move_id': fields.many2one('stock.move','Move')
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

