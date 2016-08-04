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

class load_purchase(osv.osv_memory):
    _name = "purchase.prorate.load"
    _columns = {
        'purchase_ids': fields.many2many('purchase.order','load_purchase_rel','l_id','p_id','Purchase Order'),
        'company_id': fields.many2one('res.company','Company'),
        'prorate_id': fields.many2one('stock.prorate','Prorate')
    }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(load_purchase, self).default_get(cr, uid, fields, context=context)
        prorate_id = context.get('active_id',False)
        company_id = context.get('prorate_company_id',False)
        res.update(prorate_id=prorate_id,company_id=company_id)
        return res
    
    def onchange_purchase_ids(self,cr, uid, ids,prorate_id,company_id, purchase_ids,context=None):
        result = {'domain':{}}
        prorate_pool = self.pool.get("stock.prorate")
        purchase_line_pool = self.pool.get('purchase.order.line')
        prorate_obj = prorate_pool.browse(cr, uid, prorate_id)
        purchase_dict = {}
        if prorate_obj.type =='i18n':
            move_pool = self.pool.get('stock.move')
            domain = [('state','not in',['done','cancel']),('purchase_line_id','!=',False),
                      '|',('company_id','=',False),('company_id','=',company_id),
                      '|',('prorate_id','=',False),('prorate_id','=',prorate_id)]
            move_ids = move_pool.search(cr, uid, domain)
            for move in move_pool.browse(cr, uid, move_ids):
                if move.purchase_line_id.order_id.id not in purchase_dict:
                    purchase_dict[move.purchase_line_id.order_id.id] = True
            domain2 = [('order_id.state','=','approved'),#'|',('product_id','=',False),('product_id.type','=','service')
                       ('product_id.type','=','service'),('local_prorate_id','=',False),
                       '|',('company_id','=',False),('company_id','=',company_id),
                       '|',('prorate_id','=',False),('prorate_id','=',prorate_id),]
            purchase_line_ids = purchase_line_pool.search(cr, uid, domain2)
            for purchase_line in purchase_line_pool.browse(cr, uid, purchase_line_ids):
                if purchase_line.order_id.id not in purchase_dict:
                    purchase_dict[purchase_line.order_id.id] = True
        else:
            domain1 = [('order_id.state','=','approved'),('prorate_id','=',False),
                       ('product_id.type','!=','service'),
                       '|',('company_id','=',False),('company_id','=',company_id),
                       '|',('local_prorate_id','=',False),('local_prorate_id','=',prorate_id),]
            purchase_line_ids1 = purchase_line_pool.search(cr, uid, domain1)
            for purchase_line in purchase_line_pool.browse(cr, uid, purchase_line_ids1):
                if purchase_line.order_id.id not in purchase_dict:
                    purchase_dict[purchase_line.order_id.id] = True
            domain2 = [('order_id.state','=','approved'),('prorate_id','=',False),
                       '|',('product_id','=',False),('product_id.type','=','service'),
                       '|',('company_id','=',False),('company_id','=',company_id),
                       '|',('local_prorate_id','=',False),('local_prorate_id','=',prorate_id),]
            purchase_line_ids = purchase_line_pool.search(cr, uid, domain2)
            for purchase_line in purchase_line_pool.browse(cr, uid, purchase_line_ids):
                if purchase_line.order_id.id not in purchase_dict:
                    purchase_dict[purchase_line.order_id.id] = True
#         if not prorate_id:
#             domain.extend([()])
#         move_ids = move_pool.browse(cr, uid, [('state','!=',done)])
#         domain = [('state','=','approved'),'|',('company_id','=',False),('company_id','=',company_id)]
#         
#         if not prorate_id:
#             domain.extend([('order_line.prorate_id','=',False),'|',
#                            ('order_line.move_ids','=',False),'&',
#                            ('order_line.move_ids.state','not in',['done','cancel'])
#                            ('order_line.move_ids.prorate_id','=',False)])
#         else:
#             domain.extend(['|',('order_line.prorate_id','=',False),('order_line.prorate_id','=',prorate_id),
#                            '|',('order_line.move_ids','=',False),'&',
#                            ('order_line.move_ids.state','not in',['done','cancel']),'|',
#                            ('order_line.move_ids.prorate_id','=',False),
#                            ('order_line.move_ids.prorate_id','=',prorate_id)])
#         purchases = purchase_pool.search(cr, uid, domain)
        result['domain'].update({'purchase_ids':[('id','in',purchase_dict.keys())]})
            
        return result
    
    def load_purchase_orders(self,cr, uid, ids, context=None):
        prorate_pool = self.pool.get('stock.prorate')
        for wiz_obj in self.browse(cr, uid, ids, context):
            prorate_pool.write(cr, uid, wiz_obj.prorate_id.id,{'purchase_ids':[(6,0,[p.id for p in wiz_obj.purchase_ids ])]})
            prorate_pool.load_purchases(cr, uid, [wiz_obj.prorate_id.id], context)
        return True
load_purchase()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
