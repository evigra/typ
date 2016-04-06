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
from openerp.osv import osv, fields
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_compare
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"
    
    def split(self, cr, uid, ids, move_ids, context=None):
        res = super(split_in_production_lot, self).split(cr, uid, ids,move_ids, context=context)
        if context is None: context = {}
        stockable_line_pool = self.pool.get("stock.prorate.stock.line")
        move_pool = self.pool.get('stock.move')
        prorate_pool = self.pool.get('stock.prorate')
        if not context.get('call_from_prorate',False) or not context.get('cntxt_stockable_prorate_id',False):
            return res
        stockable_line_obj = stockable_line_pool.browse(cr, uid, context['cntxt_stockable_prorate_id'], context)
        total_qty = stockable_line_obj.sent_qty
        for move_obj in move_pool.browse(cr, uid, res, context):
            prorate = prorate_pool.browse(cr, uid, context.get('cntxt_prorate_id',False))
            stockable_line_defaults = {'move_id':move_obj.id,
                                       'sent_qty':move_obj.product_qty,
                                       'prodlot_id':move_obj.prodlot_id and move_obj.prodlot_id.id or False}
            new_stockable_id = stockable_line_pool.copy(cr, uid, context['cntxt_stockable_prorate_id'],
                                                        stockable_line_defaults)
            total_qty -= move_obj.product_qty
        stockable_line_dict = {}
        if res:
            stockable_line_dict = {'sent_qty':total_qty}
        if stockable_line_obj.prodlot_id:
            if stockable_line_obj.prodlot_id.id != stockable_line_obj.move_id.prodlot_id.id:
                stockable_line_dict.update({'prodlot_id':stockable_line_obj.move_id.prodlot_id.id or False})
        else:
            stockable_line_dict.update({'prodlot_id':stockable_line_obj.move_id.prodlot_id.id or False})
        stockable_line_pool.write(cr, uid, context['cntxt_stockable_prorate_id'],stockable_line_dict)
        if res:
            prorate_pool.write(cr, uid, context.get('cntxt_prorate_id',False),{'update_needed':True})
            prorate_pool.update_stockable_lines(cr, uid, context.get('cntxt_prorate_id',False))
            move_pool.write(cr, uid, res,{'prorate_id':context.get('cntxt_prorate_id',False)})
        return res
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
