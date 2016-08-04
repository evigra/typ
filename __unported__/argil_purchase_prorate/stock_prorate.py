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

class stock_prorate(osv.osv):
    _name = "stock.prorate"
    _columns = {
        'date': fields.datetime('Date'),
        'name':fields.char('Reference',size=64, required=True),
        'purchase_ids': fields.many2many('purchase.order','purchase_prorate_rel','sp_id','po_id','Purchase Orders'),
        'service_prorate_ids': fields.one2many('stock.prorate.service.line','prorate_id','Service Lines',),
        'stock_prorate_ids':  fields.one2many('stock.prorate.stock.line','prorate_id','Stockable Lines'),
        'total_expense': fields.float('Total Expenses',digits_compute=dp.get_precision('Account'),),
        'total_stockable_amount': fields.float('Total stockable Amount',digits_compute=dp.get_precision('Account'),),
        'company_id':fields.many2one('res.company','Company',required=True),
        'currency_id': fields.many2one('res.currency','Company Currency'),
        'update_needed': fields.boolean('Need to Update'),
        'state': fields.selection([('draft','Draft'),('confirm','Purchase Loaded'),('done','Done'),('cancel','Cancelled')],'Status'),
        'valuation_account_id': fields.many2one('account.account',"Stock Valuation Account",
            help="When real-time inventory valuation is enabled on a product, "\
            "this account will hold the current value of the products."),
        'expense_account_move_id' : fields.many2one('account.move', 'Account Move'),
        'global_currency_rate': fields.float('Global Currency Rate',digits=(12,6),),
        'update_currency_rate': fields.boolean('Update Currency Rate'),
        'type': fields.selection([('l10n','Local Prorate'),('i18n','International Prorate')],
                                 'Type', readonly=True, select=True, change_default=True),

    }

    def _get_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('type', 'i18n')
    
    _defaults = {
        'name':'/',
        'update_needed': True,
        'date': fields.datetime.now,
        'state': 'draft',
        'currency_id': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.id,
        'global_currency_rate':lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.currency_id.rate or 1.00,
        'company_id': lambda self, cr, uid, ctx: self.pool.get('res.company')._company_default_get(cr, uid,context=ctx),
        'type':_get_type,
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for prorate in self.browse(cr, uid, ids, context):
            if prorate.state not in ('draft','confirm','cancel'):
                raise osv.except_osv(_('Error!'), _('You cannot delete a confirmed record.'))
        return super(stock_prorate, self).unlink(cr, uid, ids, context=context)
    
    def copy(self, cr, uid, id, default=None, context=None):
        if context is None:context={}
        if default is None: default = {}
        default.update({   
            'update_needed': True,
            'purchase_ids':[(6,0,[])],
            'service_prorate_ids': [],
            'stock_prorate_ids': [],
            'state':'draft',
            'name':'/',
            'date': fields.datetime.now(),
            'global_currency_rate': self.pool.get('res.users').browse(cr, uid, uid, context).company_id.currency_id.rate or 1.00,
            'update_currency_rate': False,
        })
        new_id = super(stock_prorate, self).copy(cr, uid, id, default, context=context)
        return new_id
    
#     def cancel_local_prorate(self, cr, uid, ids, context=None):
#         for prorate_obj in self.browse(cr, uid, ids, context):
#             for stockable_line in prorate_obj.stock_prorate_ids:
#                 stockable_line.purchase_line_id.write({'loc_inc_price_unit':stockable_line.new_price_unit})
#                 if not stockable_line.representation_percent:
#                     pass
#                 total_representation += stockable_line.representation_percent
#             if round(total_representation,3) != 100.00:
#                 raise osv.except_osv(_('Warning!'), _('Proprate Representation is not 100% complete.'))
#             prorate_obj.write({'state':'done',})
#         self.write(cr, uid, ids, {'state':'cancel'})
#         return True
    
    def onchange_global_rate(self, cr, uid, ids, global_rate,context=None):
        return {'value':{'update_needed': True,'update_currency_rate': True}}
    
    def button_load_purchases(self, cr, uid, ids, context=None):
        if context is None: context={}
        prorate = self.browse(cr, uid, ids, context)[0]
        context.update({'active_id': ids and ids[0] or False,
                        'prorate_company_id':prorate.company_id.id,
                        'default_purchase_ids':False})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'purchase.prorate.load',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'name': 'Load Purchase Orders',
            'context': context
        }
        
    def load_purchases(self, cr, uid, ids, context=None):
        if context is None: context={}
        purchase_pool = self.pool.get('purchase.order')
        purchase_line_pool = self.pool.get('purchase.order.line')
        move_pool = self.pool.get('stock.move')
        if isinstance(ids, (int, long)):
            ids = [ids]
        for prorate_obj in self.browse(cr, uid, ids, context):
            if context.get('reload_purchase',False):
                self.pool.get('stock.prorate.service.line').unlink(cr, uid,[service_prorate.id \
                                            for service_prorate in prorate_obj.service_prorate_ids])
                self.pool.get('stock.prorate.stock.line').unlink(cr, uid,[stock_prorate.id \
                                            for stock_prorate in prorate_obj.stock_prorate_ids])
            to_write_purchase = []
            to_write_move = []
            purchase_ids = [p.id for p in prorate_obj.purchase_ids]
            if not purchase_ids:
                raise osv.except_osv(_('Warning!'), _('Please specify purchase orders to load.'))
            company_id = prorate_obj.company_id.id
            currency_id = prorate_obj.currency_id.id
            cntxt = context.copy()
            cntxt.update({'global_curr_rate':prorate_obj.global_currency_rate,
                          'update_global_rate':prorate_obj.update_currency_rate})
            total_services,total_stockable_amount,service_lines, stockable_lines = self.get_prorate_lines(cr, 
                                                    uid, [prorate_obj.id],purchase_ids,company_id,currency_id,context=cntxt)
            if not stockable_lines:
                raise osv.except_osv(_('No stockable lines!'), _('Please add purchase orders with stockable products.'))
            prorate_obj.write({'service_prorate_ids': map(lambda x:(0,0, x),service_lines),
                               'stock_prorate_ids':map(lambda x:(0,0, x),stockable_lines),
                               'total_expense':total_services,
                               'total_stockable_amount':total_stockable_amount,
                               'state':'confirm','update_needed':False})
            for purchase in purchase_pool.browse(cr, uid, purchase_ids, context):
                for line in purchase.order_line:
                    if not line.move_ids:
                        to_write_purchase.append(line.id)
                        continue
                    move_count = 1
                    for move in line.move_ids:
                        if move.state in ('done','cancel'):
                            move_count +=1
                            continue
                        to_write_move.append(move.id)
                    if len(line.move_ids) == move_count:
                        to_write_purchase.append(line.id)
            if to_write_purchase:
                if prorate_obj.type == 'i18n':
                    purchase_line_pool.write(cr, uid,to_write_purchase,{'prorate_id':prorate_obj.id} )
                else:
                    purchase_line_pool.write(cr, uid,to_write_purchase,{'local_prorate_id':prorate_obj.id} )
            if to_write_move and prorate_obj.type == 'i18n':
                move_pool.write(cr, uid, to_write_move,{'prorate_id':prorate_obj.id})
            if prorate_obj.name == '/':
                if prorate_obj.type == 'i18n':
                    prorate_obj.write({'name':self.pool.get('ir.sequence').get(cr, uid, 'stock.prorate')})
                else:
                    prorate_obj.write({'name':self.pool.get('ir.sequence').get(cr, uid, 'stock.prorate.loc')})
        return True
    
    def create_account_valuation_moves(self, cr, uid, ids, context=None):
        account_move_pool = self.pool.get('account.move')
        stock_location_pool = self.pool.get('stock.location')
        account_fiscal_pool = self.pool.get('account.fiscal.position')
        ir_values = self.pool.get('ir.values')
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        period_id = account_move_pool._get_period(cr, uid,context=context)
        for prorate_obj in self.browse(cr, uid, ids, context):
            valuation_account_id = ir_values.get_default(cr, uid, 'stock.prorate', 
                                    'valuation_account_id', company_id=prorate_obj.company_id.id)
            move_lines = []
            line = prorate_obj.stock_prorate_ids[0]
            for service_line in prorate_obj.service_prorate_ids:
                po_line = service_line.purchase_line_id
                prod_account = po_line.product_id.property_account_expense.id or po_line.product_id.categ_id.property_account_expense_categ.id or False
                if not prod_account:
                    raise osv.except_osv(_('Warning !'),
                        _('Expense Account is not defined for product %s') % \
                            (po_line.product_id.name,))
                move_line = (0,0, {
                    'name': _('Reclassification of expenditure: ') + service_line.purchase_id.name + ' - ' + po_line.name,
                    'ref': service_line.purchase_id.name + ' - ' + po_line.name,
                    'product_id': po_line.product_id.id,
                    'product_uom_id': po_line.product_uom.id,
                    'account_id': account_fiscal_pool.map_account(cr, uid, False, prod_account),
                    'debit': 0.0,
                    'credit': round(po_line.price_subtotal, precision),
                    'quantity': po_line.product_qty,
                    'journal_id': line.product_id.categ_id.property_stock_journal.id,
                    'period_id': period_id,
                    })
                move_lines.append(move_line)
            if move_lines:
                move_line = (0,0, {
                        'name': _('Reclassification of expenditure: ') + prorate_obj.name,
                        'ref': prorate_obj.name,
                        'account_id'        : account_fiscal_pool.map_account(cr, uid, False, valuation_account_id),
                        'journal_id'        : line.product_id.categ_id.property_stock_journal.id,
                        'period_id'         : period_id,
                        })
                move_lines.append(move_line)
                account_move = {
                        'period_id'     : period_id,
                        'date'          : context.get('date', fields.date.context_today(self,cr,uid,context=context)),
                        'journal_id'    : line.product_id.categ_id.property_stock_journal.id,
                        'line_id'       : move_lines,
                        'ref'           : prorate_obj.name,
                        }
                move_id = account_move_pool.create(cr, uid, account_move, context=context)
                self.write(cr, uid, [prorate_obj.id], {'expense_account_move_id': move_id})
        return True
    
    def process_prorate(self, cr, uid, ids, context=None):
        for prorate_obj in self.browse(cr, uid, ids, context):
            total_representation = 0.0
            for stockable_line in prorate_obj.stock_prorate_ids:
                stockable_line.purchase_line_id.write({'loc_inc_price_unit':stockable_line.new_price_unit})
                if not stockable_line.representation_percent:
                    pass
                total_representation += stockable_line.representation_percent
            if round(total_representation,3) != 100.00:
                raise osv.except_osv(_('Warning!'), _('Proprate Representation is not 100% complete.'))
            prorate_obj.write({'state':'done',})
        return True
    
    def receive_products(self, cr, uid, ids, context=None):
        if context is None: context={}
        purchase_pool = self.pool.get('purchase.order')
        move_pool = self.pool.get('stock.move')
        partial_picking_pool = self.pool.get('stock.partial.picking')
        partial_picking_dict={}
        ir_values = self.pool.get('ir.values')
        self.update_stockable_lines(cr, uid, ids, context)
        for prorate_obj in self.browse(cr, uid, ids, context):
            valuation_account_id = ir_values.get_default(cr, uid, 'stock.prorate', 
                                    'valuation_account_id', company_id=prorate_obj.company_id.id)
            if not valuation_account_id:
                raise osv.except_osv(_('Configuration Error!'),_('Please contact Administrator to set Valuation Account for your company'))
            partial_move_data = []
            total_representation = 0.0
            for stockable_line in prorate_obj.stock_prorate_ids:
                if stockable_line.product_id.track_incoming and not stockable_line.prodlot_id:
                    raise osv.except_osv(_('Serial Number not specified!'),_('Please specify serial number for the product %s.'%(stockable_line.product_id.name)))
                partial_move_dict = {
                    'product_id' : stockable_line.product_id.id,
                    'quantity' : stockable_line.sent_qty,
                    'product_uom' : stockable_line.sent_uom_id.id,
                    'prodlot_id' : stockable_line.prodlot_id and stockable_line.prodlot_id.id or False,
                    'move_id' : stockable_line.move_id.id,
                    'location_id' : stockable_line.move_id.location_id.id,
                    'location_dest_id' : stockable_line.move_id.location_dest_id.id,
                    'update_cost':stockable_line.sent_qty and True or False,
                    'cost': stockable_line.sent_qty and (stockable_line.total_incl_prorate / stockable_line.sent_qty) or 0.0,
                    'currency': prorate_obj.currency_id.id or stockable_line.currency_id.id or \
                                    stockable_line.move_id.picking_id.currency_id.id or False
                    }
                    
                partial_move_data.append(partial_move_dict)
                if stockable_line.move_id.picking_id.id not in partial_picking_dict:
                    partial_picking_dict[stockable_line.move_id.picking_id.id] = [partial_move_dict]
                else:
                    partial_picking_dict[stockable_line.move_id.picking_id.id].append(partial_move_dict)
                if not stockable_line.representation_percent:
                    pass
#                     raise osv.except_osv(_('Warning!'), _('Please specify purchase orders to load.'))
                total_representation += stockable_line.representation_percent
            if round(total_representation,3) != 100.00:
                raise osv.except_osv(_('Warning!'), _('Proprate Representation is not 100% complete.'))
            for picking_id in partial_picking_dict:
                cntxt= context.copy()
                cntxt.update({'active_model':'stock.picking','active_ids':[picking_id]})
                partial_picking_id = partial_picking_pool.create(cr, uid, {'date':prorate_obj.date,
                                                                 'move_ids': map(lambda x:(0,0,x),partial_picking_dict[picking_id]),
                                                                 'picking_id':picking_id}, context=cntxt)
                partial_picking_pool.do_partial(cr, uid, [partial_picking_id], context=cntxt)
            
            self.create_account_valuation_moves(cr, uid, ids, context)
            prorate_obj.write({'state':'done',})
        return True
    
    def onchange_purchase_ids(self,cr, uid, ids, purchase_ids,context=None):
        result = {'domain':{}}
#         purchase_pool = self.pool.get('purchase.order')
#         domain = [('state','=','approved'),('shipped','!=',False)]
#         if not ids:
#             domain.append(('prorate_id','=',False))
#         else:
#             domain.extend(['|',('prorate_id','=',False),('prorate_id','in',ids)])
#         purchases = purchase_pool.search(cr, uid, domain)
#         result['domain'].update({'purchase_ids':[('id','in',purchases)]})
            
        return result
    
    def get_prorate_lines(self, cr, uid, ids,purchase_ids,company_id,currency_id, context=None):
        service_lines = []
        stockable_lines = []
        total_services = 0.0
        total_stockable_amount = 0.0
        purchase_line_pool = self.pool.get('purchase.order.line')
        currency_pool = self.pool.get('res.currency')
        product_pool = self.pool.get('product.product')
        uom_pool = self.pool.get('product.uom')
        purchase_line_ids = purchase_line_pool.search(cr, uid, [('order_id','in',purchase_ids),])
        prorate_obj = self.browse(cr, uid, ids, context=context)[0]
        for line_obj in purchase_line_pool.browse(cr, uid, purchase_line_ids,context=context):
            unit_price = line_obj.price_unit
            price_subtotal = line_obj.price_subtotal
            line_currency_id = line_obj.order_id.currency_id.id or False
            if prorate_obj.type == 'i18n' and line_obj.local_prorate_id:
                if line_obj.product_id.type == 'service':
                    continue
                unit_price = line_obj.loc_inc_price_unit
                price_subtotal = line_obj.loc_inc_price_unit * line_obj.product_qty
                line_currency_id = line_obj.local_currency_id and line_obj.local_currency_id.id or \
                        line_obj.order_id.currency_id.id or False
            service_dict,stockable_dict = {},{}
#             if prorate_obj.type == 'l10n':
                
            ctx = context.copy()
            ctx['date'] = line_obj.date_planned
            purchase_currency_id = line_currency_id or line_obj.order_id.currency_id.id or False
            price_total_company_curr = currency_pool.compute(cr, uid, purchase_currency_id,
                                            currency_id, price_subtotal, context=ctx)
            price_unit_company_curr = currency_pool.compute(cr, uid, purchase_currency_id,
                                            currency_id, unit_price, context=ctx)
            currency_obj = currency_pool.browse(cr, uid, [purchase_currency_id,currency_id],context=ctx)
            line_dict = {
                'name': "%s%s"%(line_obj.local_prorate_id and line_obj.local_prorate_id.name+': 'or '',line_obj.name),
                'purchase_line_id':line_obj.id,
                'purchase_id':line_obj.order_id.id,
                'product_id':line_obj.product_id and line_obj.product_id.id or False,
                'price_unit':unit_price,
                'uom_id':line_obj.product_uom and line_obj.product_uom.id or False,
                'qty':line_obj.product_qty,
                'total': price_subtotal,
                'company_id':line_obj.order_id.company_id.id or False,
                'currency_id': line_currency_id or False,
                'currency_rate':currency_pool._get_conversion_rate(cr, uid, 
                                            currency_obj[0], currency_obj[1], context=ctx),
                'total_in_company_currency': price_total_company_curr,
                'date_planned':line_obj.date_planned,
            }
            update_global_rate = context.get('update_global_rate',False)
            if not update_global_rate:
                if line_dict['currency_rate'] != context.get('global_curr_rate',0.0):
                    update_global_rate = True
            if update_global_rate:
                global_currency_rate = context.get('global_curr_rate',0.0)
                price_total_company_curr = global_currency_rate * price_subtotal
                
                line_dict.update({
                    'total_in_company_currency':price_total_company_curr,
                    'currency_rate':global_currency_rate,
                })
            if not line_obj.product_id or line_obj.product_id.type  not in ('product', 'consu'):
                service_dict = line_dict.copy()
                service_lines.append(service_dict)
                total_services += price_total_company_curr
            else:
                for move_obj in line_obj.move_ids:
                    if move_obj.state in ('done','cancel'):
                        continue
                    stockable_dict = line_dict.copy()
                    stockable_dict.update({
                        'move_id': move_obj.id,
                        'sent_uom_id': move_obj.product_uom and move_obj.product_uom.id or False,
                        'sent_qty': move_obj.product_qty,
                        #TODO uom
                        'sent_total':move_obj.product_qty * price_unit_company_curr,
                        'prodlot_id':move_obj.prodlot_id and  move_obj.prodlot_id.id or False,
#                         'representation_percent': 
                    })
                    if update_global_rate:
                        global_currency_rate = context.get('global_curr_rate',0.0)
                        price_unit_company_curr = global_currency_rate * unit_price
                        stockable_dict.update({
                            'sent_total':move_obj.product_qty * price_unit_company_curr,
                        })
                    stockable_lines.append(stockable_dict)
                    total_stockable_amount +=move_obj.product_qty * price_unit_company_curr
        for stockable_line in stockable_lines:
            representation = (stockable_line['sent_total']/total_stockable_amount)
            prorated_expense = total_services *representation
            total_incl_prorate = stockable_line['sent_total'] + prorated_expense
            product = product_pool.browse(cr, uid, stockable_line['product_id'])
            avail_qty = product.qty_available
            cntxt = context.copy()
            cntxt.update({'currency_id':prorate_obj.currency_id.id})
            qty = uom_pool._compute_qty(cr, uid, stockable_line['sent_uom_id'], 
                                    stockable_line['sent_qty'], product.uom_id.id)
#         new_price = currency_obj.compute(cr, uid, product_currency,
#                 move_currency_id, product_price, round=False)
            new_amount = uom_pool._compute_price(cr, uid, stockable_line['sent_uom_id'], 
                                                 total_incl_prorate, product.uom_id.id)
            #any change should affect in onchange representation also
            pricetype_obj = self.pool.get('product.price.type')
            price_type_id = pricetype_obj.search(cr, uid, [('field','=','standard_price')])[0]
            price_type_currency_id = pricetype_obj.browse(cr,uid,price_type_id).currency_id.id
            amount_unit = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                    cntxt['currency_id'], stockable_line['price_unit'],context=context)
#             amount_unit = product.price_get('standard_price', context=cntxt)[product.id]#TODO need to pass currecny
            new_price_unit = ((amount_unit * avail_qty) + (new_amount))/(avail_qty + qty)
            stockable_line.update({
                'representation_percent': representation*100.0,
                'prorated_expense': prorated_expense,
                'total_incl_prorate': total_incl_prorate,
                'new_price_unit': new_price_unit})
        return total_services,total_stockable_amount, service_lines,stockable_lines
    
    def onchange_service_prorate_ids(self, cr, uid, ids, service_prorate_ids,context=None):
        result = {'value':{}}
        service_pool = self.pool.get("stock.prorate.service.line")
        service_prorate_ids = resolve_o2m_operations(cr, uid, service_pool, service_prorate_ids, ['total_in_company_currency'], context)
        total_expense = 0.0
        for service_line in service_prorate_ids:
            total_expense += service_line['total_in_company_currency']
        result['value'].update({'total_expense':total_expense,'update_needed':True})
        return result
    
    def onchange_stockable_prorate_ids(self, cr, uid, ids, stock_prorate_ids,total_expense,currency_id,context=None):
        result = {'value':{}}
        stock_prorate_pool = self.pool.get("stock.prorate.stock.line")
        stock_prorate_datas = resolve_o2m_operations(cr, uid, stock_prorate_pool, stock_prorate_ids, ['sent_total'], context)
        total_stockable_amount = 0.0
        for stockable_line in stock_prorate_datas:
            total_stockable_amount += stockable_line['sent_total']
        result['value'].update({'total_stockable_amount':total_stockable_amount,'update_needed':True})
        #sent_total/stockable_amount
#         result['value'].update({'stock_prorate_ids': self.o2m_stockable_update(cr, uid, 
#                                 stock_prorate_ids,total_stockable_amount,total_expense,currency_id,context)
#                                 })
        return result
    
    
    def update_stockable_lines(self, cr, uid, ids, context=None):
        stockable_prorate_pool = self.pool.get("stock.prorate.stock.line")
        if isinstance(ids, (int, long)):
            ids = [ids]
        for prorate in self.browse(cr ,uid, ids, context):
            if not prorate.update_needed and not prorate.update_currency_rate:
                continue
            total_expense = 0.0
            total_stockable_amount = 0.0
            currency_flag = False
            if prorate.update_currency_rate:
                currency_flag =True
                for service_prorate in prorate.service_prorate_ids:
                    total_in_company_currency = prorate.global_currency_rate * service_prorate.total
                    service_prorate.write({
                        'currency_rate':prorate.global_currency_rate,
                        'total_in_company_currency':total_in_company_currency
                    })
                    total_expense += total_in_company_currency
                    service_prorate.refresh()
                for stock_prorate in prorate.stock_prorate_ids:
                    sent_total = prorate.global_currency_rate * stock_prorate.price_unit * stock_prorate.sent_qty
                    stock_prorate.write({
                        'currency_rate':prorate.global_currency_rate,
                        'total_in_company_currency':prorate.global_currency_rate * stock_prorate.total,
                        'sent_total': sent_total
                    })
                    total_stockable_amount += sent_total
                    stock_prorate.refresh()
                prorate.write({'total_stockable_amount':total_stockable_amount,'total_expense':total_expense})
                prorate.refresh()
                
#         for prorate in self.browse(cr ,uid, ids, context):
            for stock_prorate in prorate.stock_prorate_ids:
                if not stock_prorate.sent_total:
                    continue
                
                prorate_currency_id = prorate.currency_id.id
                stock_currency_id = stock_prorate.currency_id.id
                currency_rate = stock_prorate.currency_rate
                if currency_flag:
                    currency_rate = prorate.global_currency_rate
                    prorate_currency_id = False
                    stock_currency_id = False
                res = stockable_prorate_pool.onchange_sent_qty(cr, uid, [], 
                                stock_prorate.price_unit, stock_prorate.sent_qty,
                                stock_currency_id,prorate_currency_id,stock_prorate.date_planned,currency_rate)['value']
                
                representation = (res['sent_total']/prorate.total_stockable_amount)*100.0
                res.update(stockable_prorate_pool.onchange_representation(cr, uid, [],
                        stock_prorate.product_id.id,stock_prorate.uom_id.id,stock_prorate.sent_uom_id.id,
                        stock_prorate.sent_qty,stock_prorate.price_unit,prorate.total_expense,stock_prorate.sent_total,
                        representation,stock_currency_id,prorate_currency_id, context)['value'])
                res.update({'representation_percent':representation})
                stock_prorate.write(res)
            prorate.write({'update_needed':False,'update_currency_rate':False})
        return True
    
stock_prorate()

class stock_prorate_service_line(osv.osv):
    _name = "stock.prorate.service.line"
    _columns = {
        'prorate_id': fields.many2one('stock.prorate','Prorate'),
        'name':fields.char('Description',size=128),
        'purchase_line_id':fields.many2one('purchase.order.line','Purchase Line'),
        'purchase_id': fields.many2one('purchase.order',"Purchase order"),
        'product_id':fields.many2one('product.product','Product'),
        'uom_id':fields.many2one('product.uom','UoM'),
        'price_unit':fields.float('Price Unit',digits_compute= dp.get_precision('Product Price')),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Product Unit of Measure'),),
        'total':fields.float('Amount',digits_compute=dp.get_precision('Account'),),
        'company_id':fields.many2one('res.company','Company',required=True),
        'currency_id': fields.many2one('res.currency','Currency'),
        'date_planned': fields.datetime('Date Planned'),
        'currency_rate': fields.float('Currency Rate',digits=(12,6),),
        'total_in_company_currency': fields.float('Amount In Company Currency',digits_compute=dp.get_precision('Account'),)
    }
    
    def onchange_rate(self, cr, uid, ids, currency_rate,total, context=None):
        result = {'value':{}}
        result['value'].update({'total_in_company_currency':currency_rate *total})
        return result
    
stock_prorate_service_line()

class stock_prorate_stockable_line(osv.osv):
    _name = "stock.prorate.stock.line"
    _columns = {
        'prorate_id': fields.many2one('stock.prorate','Prorate'),
        'name':fields.char('Description',size=128),
        'purchase_line_id':fields.many2one('purchase.order.line','Purchase Line'),
        'purchase_id': fields.many2one('purchase.order',"Purchase order"),
        'product_id':fields.many2one('product.product','Product'),
        'uom_id':fields.many2one('product.uom','UoM'),
        'move_id':fields.many2one('stock.move','Move'),
        'representation_percent':fields.float('Representation (%)'),
        'prorated_expense':fields.float('Prorated Expense'),
        'date_planned': fields.datetime('Date Planned'),
        'price_unit':fields.float('Price Unit',digits_compute= dp.get_precision('Product Price')),
        'qty':fields.float('Qty',digits_compute=dp.get_precision('Product Unit of Measure'),),
        'total':fields.float('Amount',digits_compute=dp.get_precision('Account'),),
        'total_in_company_currency': fields.float('Amount In Company Currency',digits_compute=dp.get_precision('Account'),),
        'sent_uom_id':fields.many2one('product.uom','Sent UoM'),
        'sent_qty':fields.float('Qty sent',digits_compute=dp.get_precision('Product Unit of Measure'),),
        'sent_total': fields.float('Amount as per qty sent',digits_compute=dp.get_precision('Account'),),
        'total_incl_prorate':fields.float('Amount + Prorate',digits_compute=dp.get_precision('Account'),),
        
        'new_price_unit':fields.float('New Unit Price',digits_compute= dp.get_precision('Product Price')),
        'company_id':fields.many2one('res.company','Company',required=True),
        'currency_id': fields.many2one('res.currency','Currency'),
        'currency_rate': fields.float('Currency Rate',digits=(12,6),),
#         'available_qty': fields.float('Available Qty')
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number')
    }

    def onchange_rate(self, cr, uid, ids, currency_rate,price_unit,sent_qty,total, context=None):
        result = {'value':{}}
        result['value'].update({'total_in_company_currency':currency_rate *total,
                                'sent_total': currency_rate *price_unit * sent_qty})
        return result
    
    def onchange_sent_qty(self,cr, uid, ids, price_unit,sent_qty,from_currency,
                          to_currency,date,currency_rate=1.0, context=None):
        #added currency rate so that if any of the currency is not specified, 
        #then this currency rate will be considered, mainly useful in update purchase order function update_stockable_lines
        result = {'value':{}}
        ctx = {}
        ctx['date'] = date or False
        currency_pool = self.pool.get('res.currency')
        if from_currency != to_currency:
            price_unit_company_curr = currency_pool.compute(cr, uid, from_currency,
                                            to_currency, price_unit, context=ctx)
            sent_total = price_unit_company_curr * sent_qty
        else:
            sent_total = price_unit * sent_qty * currency_rate
        result['value'].update({'sent_total': sent_total})
        if not sent_qty:
            return result #TODO add warning if no sent qty 
        return result
    
    def onchange_sent_total(self, cr, uid, ids, sent_total,stockable_amount,context=None):
        result ={'value':{}}
        if sent_total and stockable_amount:
            result['value'].update({'representation_percent':(sent_total/stockable_amount)*100.0})
        return result
    
    def onchange_representation(self, cr, uid, ids,product_id,uom_id,sent_uom_id,
                                sent_qty,price_unit,expense,total,representation,from_currency,to_currency, context=None):
        result = {'value':{}}
        if context is None: context={}
        if not representation or not product_id:
            pass#todo
        product_pool = self.pool.get('product.product')
        uom_pool = self.pool.get('product.uom')
        prorated_expense = expense *(representation/100.0)
        total_incl_prorate = total + prorated_expense
        product = product_pool.browse(cr, uid, product_id)
        avail_qty = product.qty_available
        context.update({'currency_id':to_currency})
        qty = uom_pool._compute_qty(cr, uid, sent_uom_id, sent_qty, product.uom_id.id)
#         new_price = currency_obj.compute(cr, uid, product_currency,
#                 move_currency_id, product_price, round=False)
        new_amount = uom_pool._compute_price(cr, uid, sent_uom_id, total_incl_prorate,
                product.uom_id.id)
        #any change should effect in load prorate also
        pricetype_obj = self.pool.get('product.price.type')
        price_type_id = pricetype_obj.search(cr, uid, [('field','=','standard_price')])[0]
        price_type_currency_id = pricetype_obj.browse(cr,uid,price_type_id).currency_id.id
        amount_unit = self.pool.get('res.currency').compute(cr, uid, price_type_currency_id,
                    context['currency_id'], price_unit,context=context)
        
#         amount_unit = product.price_get('standard_price', context=context)[product.id]#TODO need to pass currecny
        new_price_unit = ((amount_unit * avail_qty) + (new_amount))/(avail_qty + qty)
        result['value'].update(prorated_expense=prorated_expense,
                               total_incl_prorate=total_incl_prorate,
                               new_price_unit=new_price_unit)
        return result
    
    def unlink(self, cr, uid, ids, context=None):
        move_pool = self.pool.get('stock.move')
        for stockable_prorate in self.browse(cr, uid, ids, context):
            if stockable_prorate.move_id:
                move_pool.write(cr, uid, [stockable_prorate.move_id.id],{'prorate_id':False})
        return super(stock_prorate_stockable_line, self).unlink(cr, uid, ids, context=context)
    
    def button_split_serialnumber(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids,(int, long)):
            ids = [ids]
        stockable_line_obj = self.browse(cr, uid, ids, context)[0]
        cntxt = context.copy()
        cntxt.update({'active_model':'stock.move',
                      'active_id':stockable_line_obj.move_id and stockable_line_obj.move_id.id or False,
                      'active_ids': stockable_line_obj.move_id and [stockable_line_obj.move_id.id] or [],
                      'call_from_prorate': True,#This context is needed for reloading prorate
                      'cntxt_prorate_id':stockable_line_obj.prorate_id and stockable_line_obj.prorate_id.id or False,
                      'cntxt_stockable_prorate_id': stockable_line_obj.id or False})
        return {
              'name': _('Split In Serial Number'),
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'stock.move.split',
              'type': 'ir.actions.act_window',
#               'res_id': ids and ids[0] or False,
              'target':'new',
              'context':cntxt
              }

stock_prorate_stockable_line()

def resolve_o2m_operations(cr, uid, target_osv, operations, fields, context):
    results = []
    for operation in operations:
        result = None
        if not isinstance(operation, (list, tuple)):
            result = target_osv.read(cr, uid, operation, fields, context=context)
        elif operation[0] == 0:
            # may be necessary to check if all the fields are here and get the default values?
            result = operation[2]
        elif operation[0] == 1:
            result = target_osv.read(cr, uid, operation[1], fields, context=context)
            if not result: result = {}
            result.update(operation[2])
        elif operation[0] == 4:
            result = target_osv.read(cr, uid, operation[1], fields, context=context)
        if result != None:
            results.append(result)
    return results
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
