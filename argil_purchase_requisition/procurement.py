# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 ZestyBeanz Technologies Pvt. Ltd.
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


from openerp.osv import fields,osv
from openerp import netsvc

class procurement_order(osv.osv):

    _inherit = "procurement.order"

#     def action_po_assign(self, cr, uid, ids, context=None):
#         """ This is action which call from workflow to assign purchase order to procurements
#         @return: True
#        """
#         Flag = False
#         res = super(procurement_order, self).action_po_assign(cr, uid, ids, context=context)
#         for proc in self.browse(cr, uid, ids, context):
#             if proc.product_id.purchase_requisition:
#                flag=True
#         return res and not flag and res or 0
    def check_requisition(self, cr, uid, ids, context=None):
        ''' return True if the purchase requisition of the mto product is true
        '''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_id.purchase_requisition:
                return True
        return False


    def action_pr_assign(self, cr, uid, ids, context=None):
        """ This is action which call from workflow to assign purchase requisition to procurements
        @return: True
        """
        res = self.make_pr(cr, uid, ids, context=context)
        res = res.values()
        return len(res) and res[0] or 0 #TO CHECK: why workflow is generated error if return not integer value

    def make_pr(self, cr, uid, ids, context=None):
        res = {}
        requisition_obj = self.pool.get('purchase.requisition')
        non_requisition = []
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_id.purchase_requisition:
                user_company = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id
                req = res[procurement.id] = requisition_obj.create(cr, uid, {
                    'origin': procurement.origin,
                    'date_end': procurement.date_planned,
                    'warehouse_id': self._get_warehouse(procurement, user_company),
                    'company_id': procurement.company_id.id,

                    'line_ids': [(0, 0, {
                        'product_id': procurement.product_id.id,
                        'product_uom_id': procurement.product_uom.id,
                        'product_qty': procurement.product_qty,
                        'proc_move_id':procurement.move_id and procurement.move_id.id or False,

                    })],
                })
                procurement.write({
                    'state': 'running',
                    'requisition_id': req
                })
            else:
                non_requisition.append(procurement.id)

#         if non_requisition:
#             res.update(super(procurement_order, self).make_po(cr, uid, non_requisition, context=context))

        return res

    def reload_procurement_data(self, cr, uid, **args):
        """
        This method is called to reload procurement in running state but its moves are in done state.
        """
        # procurement_ids = self.search(cr, uid, [('state','=', 'running'),('move_id.state','=','done'),
        #                                  ('procure_method','=','make_to_order')])
        # if not procurement_ids:
        #     return True
        # self.write(cr, uid, procurement_ids, {'state':'done'})
        return True
procurement_order()

class stock_move(osv.osv):
    _inherit = "stock.move"
    def action_done(self, cr, uid, ids, context=None):
        result =super(stock_move, self).action_done(cr, uid, ids, context)
        procurement_pool = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        proc_ids = procurement_pool.search(cr, uid,[('move_id','in',ids),
                                                    ('state','=','running'),
                                                    ('requisition_id','!=',False)])
        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'subflow.pur_requisition_done', cr)
        return result

stock_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
