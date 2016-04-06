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


from openerp.osv import osv, fields
from openerp import netsvc

class stock_warehouse(osv.osv):
    _inherit = "stock.warehouse"
    _columns = {
        'dist_center_warehouse_id': fields.many2one('stock.warehouse_view', 'Distribution Center Warehouse'),
    }
stock_warehouse()

class stock_move(osv.osv):
    _inherit = "stock.move"
    def action_done(self, cr, uid, ids, context=None):
        result =super(stock_move, self).action_done(cr, uid, ids, context)
        procurement_pool = self.pool.get('procurement.order')
        wf_service = netsvc.LocalService("workflow")
        proc_ids = procurement_pool.search(cr, uid,[('move_id','in',ids),
                                                    ('state','=','running'),
                                                    ('supply_req_id','!=',False)])
        for proc_id in proc_ids:
            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'subflow.supply_request_done', cr)
        return result
    
stock_move()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: