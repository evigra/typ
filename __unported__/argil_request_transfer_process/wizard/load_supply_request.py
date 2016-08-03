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

class load_supply_request(osv.osv_memory):
    _name = "supply.request.load"
    _columns = {
        'supply_request_line_ids': fields.one2many('supply.request.load.line','wiz_id','Supply Request'),
        'company_id': fields.many2one('res.company','Company'),
        'transfer_id': fields.many2one('stock.transfer','Stock Transfer'),
        'warehouse_id': fields.many2one('stock.warehouse','Warehouse'),
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(load_supply_request, self).default_get(cr, uid, fields, context=context)
        transfer_id = context.get('active_id',False)
        company_id = context.get('transfer_company_id',False)
        warehouse_id = context.get('transfer_warehouse_id',False)
        transfer_supply_request_ids = context.get('transfer_supply_request_ids',False)
        res.update(transfer_id=transfer_id,company_id=company_id,warehouse_id=warehouse_id)
        supply_request_line_ids = self._partial_supply_request_for(cr, uid, transfer_supply_request_ids)
        res.update(supply_request_line_ids=supply_request_line_ids)
        return res
    
    def _partial_supply_request_for(self, cr, uid, supply_request_ids, context=None):
        result = []
        supply_request_pool = self.pool.get('stock.supply_request')
        
        for supply_request in supply_request_pool.browse(cr, SUPERUSER_ID, supply_request_ids):
            result.append({
                'supply_req_id': supply_request.id,
                'product_id': supply_request.product_id.id or False,
                'qty_request':supply_request.qty,
                'qty_sent': supply_request.residual,
                'product_uom_id':supply_request.product_uom_id.id or False,
                'required_date': supply_request.required_date or False,
                'from_warehouse_id': supply_request.from_warehouse_id.id or False,
                })
        return result
    
    def load_supply_request(self, cr, uid, ids, context=None):
        transfer_line_pool = self.pool.get('stock.transfer.line')
        transfer_pool = self.pool.get('stock.transfer')
        requst_pool = self.pool.get('stock.supply_request')
        wiz_obj = self.browse(cr, SUPERUSER_ID, ids, context)[0]
        for wiz_line in wiz_obj.supply_request_line_ids:
            if not wiz_line.qty_sent or not wiz_line.supply_req_id:
                continue
            transfer_line_data = {
                'transfer_id':wiz_obj.transfer_id.id or False,
                'product_id': wiz_line.product_id.id or False,
                'supply_req_id': wiz_line.supply_req_id.id or 0,
                'product_uom':wiz_line.product_uom_id.id or False,
                'qty': wiz_line.qty_sent or 0.0,
                'origin_qty':wiz_line.qty_request or 0.0,
                'standard_price':wiz_line.product_id.standard_price,
                'standard_price_dummy':wiz_line.product_id.standard_price,
                'dest_move_id':wiz_line.supply_req_id.dest_move_id.id or 0
            }
            transfer_line_id = transfer_line_pool.create(cr, uid,transfer_line_data)
            wiz_line.supply_req_id.write({'transfer_line_id':transfer_line_id,
                                       'transfer_id':wiz_obj.transfer_id.id})
        transfer_pool.button_dummy(cr, uid, [wiz_obj.transfer_id.id], context)
        return True
    
load_supply_request()

class supply_request_load_line(osv.osv_memory):
    _name = 'supply.request.load.line'
    _columns = {
        'wiz_id': fields.many2one('supply.request.load','Wizard'),
        'supply_req_id': fields.many2one('stock.supply_request','Supply Request'),
        'product_id': fields.many2one('product.product','Product'),
        'qty_request': fields.float('Qty Requested',digits_compute=dp.get_precision('Product Unit of Measure')),
        
        'qty_sent': fields.float('Qty to Send',digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_uom_id':fields.many2one('product.uom','Product UoM'),
        'required_date': fields.datetime('Required Date'),
        'from_warehouse_id': fields.many2one('stock.warehouse_view', 'Required Warehouse'),
    }
    _order = "required_date"
supply_request_load_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
