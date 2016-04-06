# # -*- encoding: utf-8 -*-
# ##############################################################################
# #
# #    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
# #    (http://wwww.zbeanztech.com)
# #    contact@zbeanztech.com
# #
# #    This program is free software: you can redistribute it and/or modify
# #    it under the terms of the GNU General Public License as published by
# #    the Free Software Foundation, either version 3 of the License, or
# #    (at your option) any later version.
# #
# #    This program is distributed in the hope that it will be useful,
# #    but WITHOUT ANY WARRANTY; without even the implied warranty of
# #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #    GNU General Public License for more details.
# #
# #    You should have received a copy of the GNU General Public License
# #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
# #
# ##############################################################################
# import time
# from openerp.osv import osv, fields
# from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
# from openerp.tools.float_utils import float_compare
# import openerp.addons.decimal_precision as dp
# from openerp.tools.translate import _
# 
# class stock_prorate_wizard(osv.osv_memory):
#     _name = "stock.partial.prorate.wizard"
#     _columns = {
#         'date': fields.datetime('Date'),
#         'service_prorate_ids': fields.one2many('stock.partial.prorate.service.line','wiz_id','Service Lines',),
#         'stock_prorate_ids':  fields.one2many('stock.partial.prorate.stock.line','wiz_id','Stockable Lines'),
#         'total_expense': fields.float('Total Expenses'),
#         'company_id':fields.many2one('res.company','Company',required=True)
#     }
#     _defaults = {
#         'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid,context=ctx),
#     }
#     
#     def default_get(self, cr, uid, fields, context=None):
#         if context is None: context = {}
#         res = super(stock_prorate_wizard, self).default_get(cr, uid, fields, context=context)
#         purchase_ids = context.get('active_ids', [])
#         active_model = context.get('active_model')
# 
#         if not purchase_ids:
#             # Partial Picking Processing may only be done for one picking at a time
#             return res
#         assert active_model in ('purchase.order',), 'Bad context propagation'
# #         purchase_id, = purchase_ids
# #         if 'picking_id' in fields:
# #             res.update(picking_id=picking_id)
# #         if 'move_ids' in fields:
# #             picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
# #             moves = [self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state not in ('done','cancel')]
# #             res.update(move_ids=moves)
#         if 'date' in fields:
#             res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
#         comapny_id = False
#         if 'company_id' in fields:
#             company_id = res['company_id']
#         if not company_id:
#             company_id = self.pool.get('res.company')._company_default_get(cr, uid,context=context),
#         total_services,service_lines, stockable_lines = self.get_prorate_lines(cr, 
#                                                         uid, purchase_ids,company_id,context=context)
# #         if not stockable_lines:
#             
#         res.update({'service_prorate_ids': service_lines,'stock_prorate_ids':stockable_lines,
#                     'total_expense':total_services,'company_id':company_id})
#         
#         return res
#     
#     def get_prorate_lines(self, cr, uid, purchase_ids,company_id,context=None):
#         service_lines = []
#         stockable_lines = []
#         total_services = 0.0
#         purchase_line_pool = self.pool.get('purchase.order.line')
#         purchase_line_ids = purchase_line_pool.search(cr, uid, [('order_id','in',purchase_ids),
#                                                                 ('company_id','=',company_id)])
#         
#         for line_obj in purchase_line_pool.browse(cr, uid, purchase_line_ids,context=context):
#             service_dict,stockable_dict = {},{}
#             line_dict = {
#                 'name': line_obj.name,
#                 'purchase_line_id':line_obj.id,
#                 'purchase_id':line_obj.order_id.id,
#                 'product_id':line_obj.product_id and line_obj.product_id.id or False,
#                 'price_unit':line_obj.price_unit,
#                 'uom_id':line_obj.product_uom and line_obj.product_uom.id or False,
#                 'qty':line_obj.product_qty,
#                 'total': line_obj.price_subtotal,
#             }
#             if not line_obj.product_id or line_obj.product_id.type  not in ('product', 'consu'):
#                 service_dict = line_dict.copy()
#                 service_lines.append(service_dict)
#                 total_services+=line_obj.price_subtotal
#             else:
#                 stockable_dict = line_dict.copy()
#                 for move_obj in line_obj.move_ids:
#                     if move_obj.state in ('done','cancel'):
#                         continue
#                     stockable_dict.update({
#                         'move_id': move_obj.id,
#                         'sent_uom_id': move_obj.product_uom and move_obj.product_uom.id or False,
#                         'sent_qty': move_obj.product_qty,
#                         #TODO uom
#                         'sent_total':move_obj.product_qty *line_obj.price_unit
#                     })
#                     stockable_lines.append(stockable_dict)
#         return total_services, service_lines,stockable_lines
# stock_prorate_wizard()
# 
# class stock_prorate_service_wizard(osv.osv_memory):
#     _name = "stock.partial.prorate.service.line"
#     _columns = {
#         'wiz_id': fields.many2one('stock.partial.prorate.wizard','Prorate'),
#         'name':fields.char('Description',size=128),
#         'purchase_line_id':fields.many2one('purchase.order.line','Purchase Line'),
#         'purchase_id': fields.many2one('purchase.order',"Purchase order"),
#         'product_id':fields.many2one('product.product','Product'),
#         'uom_id':fields.many2one('product.uom','UoM'),
#         'price_unit':fields.float('Price Unit'),
#         'qty':fields.float('Qty'),
#         'total':fields.float('Amount'),
#     }
# stock_prorate_service_wizard()
# 
# class stock_prorate_stockable_wizard(osv.osv_memory):
#     _name = "stock.partial.prorate.stock.line"
#     _columns = {
#         'wiz_id': fields.many2one('stock.partial.prorate.wizard','Prorate'),
#         'name':fields.char('Description',size=128),
#         'purchase_line_id':fields.many2one('purchase.order.line','Purchase Line'),
#         'purchase_id': fields.many2one('purchase.order',"Purchase order"),
#         'product_id':fields.many2one('product.product','Product'),
#         'uom_id':fields.many2one('product.uom','UoM'),
#         'move_id':fields.many2one('stock.move','Move'),
#         'representation_percent':fields.float('Representation(%)'),
#         'prorated_expense':fields.float('Prorated Expense'),
#         
#         'price_unit':fields.float('Price Unit'),
#         'qty':fields.float('Qty'),
#         'total':fields.float('Amount'),
#         'sent_uom_id':fields.many2one('product.uom','Sent UoM'),
#         'sent_qty':fields.float('Qty sent'),
#         'sent_total': fields.float('Amount as per qty sent'),
#         'total_incl_prorate':fields.float('Amount + Prorate'),
#         'new_price_unit':fields.float('New Unit Price'),
# #         'available_qty': fields.float('Available Qty')
#     }
#     def onchange_sent_qty(self,cr, uid, ids, price_unit,sent_qty, context=None):
#         result = {'value':{}}
#         result['value'].update({'sent_total': price_unit * sent_qty})
#         if not sent_qty:
#             return result #TODO add warning if no sent qty 
#         return result
#     
#     def onchange_representation(self, cr, uid, ids,product_id,uom_id,sent_uom_id,sent_qty,expense,total,representation, context=None):
#         result = {'value':{}}
#         if not representation or not product_id:
#             pass#todo
#         product_pool = self.pool.get('product.product')
#         uom_pool = self.pool.get('product.uom')
#         prorated_expense = expense *(representation/100.0)
#         total_incl_prorate = total + prorated_expense
#         product = product_pool.browse(cr, uid, product_id)
#         avail_qty = product.qty_available
#         qty = uom_pool._compute_qty(cr, uid, sent_uom_id, sent_qty, product.uom_id.id)
# #         new_price = currency_obj.compute(cr, uid, product_currency,
# #                 move_currency_id, product_price, round=False)
#         new_amount = uom_pool._compute_price(cr, uid, sent_uom_id, total_incl_prorate,
#                 product.uom_id.id)
#         amount_unit = product.price_get('standard_price', context=context)[product.id]#TODO need to pass currecny
#         new_price_unit = ((amount_unit * avail_qty) + (new_amount))/(avail_qty + qty)
#         result['value'].update(prorated_expense=prorated_expense,
#                                total_incl_prorate=total_incl_prorate,
#                                new_price_unit=new_price_unit)
#         return result
#     
# stock_prorate_stockable_wizard()
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
