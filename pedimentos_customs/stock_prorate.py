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

from openerp.osv import osv, fields
import time
import dateutil
import dateutil.parser
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from openerp import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import openerp
import calendar
from openerp import SUPERUSER_ID

class stock_prorate(osv.osv):
    _name = 'stock.prorate'
    _inherit ='stock.prorate'
    def _get_prorate(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=None):
            complete_name = []
            pedimentos = ""
            for line in rec.stock_prorate_ids:
                if line.pedimento_id:
                    complete_name.append(line.pedimento_id.name)

            if complete_name:
                complete_name = set(complete_name)
                for complete in complete_name:
                    pedimentos = pedimentos+complete+" "
            res[rec.id] = pedimentos
        return res
    _columns = {

        'prorate_ref': fields.function(_get_prorate, string="Pedimento Aduanal", type="char", size=512, readonly=True, store=True),

        }

    _defaults = {
        }
    _order = 'id desc' 


    def onchange_global_rate(self, cr, uid, ids, global_rate,context=None):
        return {'value':{'update_needed': True,'update_currency_rate': True}}

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
                
                ###### ACTUALIZAMOS LA CANTIDAD DE PEDIMENTO EN CASO DE RECARGAR LOS PEDIDOS #####
                ######### FORMA OPTIMIZADA QUERY SQL ##########
                cr.execute("""
                    select product_id from stock_prorate_stock_line
                    where prorate_id = %s group by product_id;
                    """, (prorate_obj.id, ))
                cr_res = cr.fetchall()
                product_list = [x[0] for x in cr_res]
                for prod in product_list:
                    cr.execute("""
                        select pedimento_id from stock_prorate_stock_line
                        where prorate_id = %s and product_id = %s group by pedimento_id;
                        """, (prorate_obj.id, prod, ))
                    cr_res = cr.fetchall()
                    pedimentos_list = [x[0] for x in cr_res]
                    for pedimento in pedimentos_list:
                        cr.execute("""
                            select sum(sent_qty) from stock_prorate_stock_line
                            where prorate_id = %s and product_id = %s 
                            and pedimento_id = %s
                            """, (prorate_obj.id, prod, pedimento, ))
                        cr_res = cr.fetchall()
                        qty_updt = cr_res[0][0] if cr_res else 0.0

                        cr.execute("""
                            update stock_production_lot_pedimento set stock_available=stock_available-%s
                            where id=%s
                            """,(qty_updt, pedimento, ))

                cr.execute("""
                    select id from stock_prorate_stock_line
                    where prorate_id = %s;
                    """, (prorate_obj.id, ))
                cr_res = cr.fetchall()
                prorate_line_ids = [x[0] for x in cr_res if x]
                cr.execute("""
                    delete from stock_prorate_stock_line where id in %s ;
                    """, (tuple(prorate_line_ids),))
                #self.pool.get('stock.prorate.stock.line').unlink(cr, uid, prorate_line_ids, context)
                # for stock_line in self.pool.get('stock.prorate.stock.line').browse(cr, uid,[stock_prorate.id \
                #                             for stock_prorate in prorate_obj.stock_prorate_ids], context=None):
                #     if stock_line.pedimento_id:
                #         qty = stock_line.sent_qty
                #         qty_pedimento = stock_line.pedimento_id.stock_available
                #         new_qty = qty_pedimento - qty
                #         stock_line.pedimento_id.write({'stock_available':new_qty})
                #     stock_line.unlink()
                #########################    FIN    ###############################
                # self.pool.get('stock.prorate.stock.line').unlink(cr, uid,[stock_prorate.id \
                #                             for stock_prorate in prorate_obj.stock_prorate_ids])
            
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
            
            for stock_new_line in stockable_lines:
                if 'purchase_line_id' in stock_new_line:
                    purchase_line_br = purchase_line_pool.browse(cr, uid,stock_new_line['purchase_line_id'], context=None)
                    if 'price_unit' in stock_new_line:
                        if stock_new_line['price_unit'] == 0.0:
                            stock_new_line['price_unit'] = purchase_line_br.price_unit
            
            prorate_obj.write({'service_prorate_ids': map(lambda x:(0,0, x),service_lines),
                               'stock_prorate_ids':map(lambda x:(0,0, x),stockable_lines),
                               'total_expense':total_services,
                               'total_stockable_amount':total_stockable_amount,
                               'state':'confirm','update_needed':False})
            
            ##### FORMA VELOZ POR QUERY SQL #####
            for purchase in purchase_ids:
                cr.execute("""
                select id from purchase_order_line where order_id = %s

                """, (purchase,))
                cr_res = cr.fetchall()
                purchase_order_line_list = [x[0] for x in cr_res if x]
                for line in purchase_order_line_list:
                    cr.execute("""
                        select purchase_line_id from stock_move where purchase_line_id = %s;
                        """, (line,))
                    cr_res = cr.fetchall()
                    if not cr_res:
                        purchase_order_line_move_list = []
                    else:
                        purchase_order_line_move_list = [x[0] for x in cr_res if x]
                    if not purchase_order_line_move_list:
                        to_write_purchase.append(line)
                        continue
                    cr.execute("""
                        select id from stock_move where purchase_line_id = %s;
                        """, (line,))
                    cr_res = cr.fetchall()
                    move_list = [x[0] for x in cr_res if x]
                    move_count = 1
                    for move in move_list:
                        cr.execute("select state from stock_move where id = %s" % move)
                        cr_res = cr.fetchall()
                        state_c = cr_res[0][0] if cr_res else ""
                        if state_c in ('done','cancel'):
                            move_count +=1
                            continue
                        to_write_move.append(move)
                    if len(purchase_order_line_move_list) == move_count:
                        to_write_purchase.append(line)

            # for purchase in purchase_pool.browse(cr, uid, purchase_ids, context):
            #     for line in purchase.order_line:
            #         if not line.move_ids:
            #             to_write_purchase.append(line.id)
            #             continue
            #         move_count = 1
            #         for move in line.move_ids:
            #             if move.state in ('done','cancel'):
            #                 move_count +=1
            #                 continue
            #             to_write_move.append(move.id)
            #         if len(line.move_ids) == move_count:
            #             to_write_purchase.append(line.id)

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
        
            ##### CHERMAN #####
                
            prorate_obj.refresh_lines()
        return True

    #### ANTES DE RECIBIR EJECUTE LA FUNCION DE ACTUALIZAR #####
    # def receive_products(self, cr, uid, ids, context=None):
        
    #     res = super(stock_prorate, self).receive_products(cr, uid, ids, context)
    #     ######### CHERMAN  ##########
    #     self.prorate.valida_stocks(cr, uid, ids, context)
    #     return res
    def receive_products(self, cr, uid, ids, context=None):
        if context is None: context={}
        purchase_pool = self.pool.get('purchase.order')
        move_pool = self.pool.get('stock.move')
        partial_picking_pool = self.pool.get('stock.partial.picking')
        partial_picking_dict={}
        ir_values = self.pool.get('ir.values')
        self.update_stockable_lines(cr, uid, ids, context)
        for prorate_obj in self.browse(cr, uid, ids, context):
            currency_company = prorate_obj.currency_id.id
            cr.execute("""
                select currency_id from stock_prorate_stock_line
                where prorate_id = %s group by currency_id;

                """ % ids[0])
            cr_res = cr.fetchall()
            currency_list = [x[0] for x in cr_res if x]

            cr.execute("""
                select UPPER(name) from res_currency
                where id in %s ;

                """, (tuple(currency_list),))
            cr_res = cr.fetchall()
            currency_list_name = [x[0] for x in cr_res if x]
            if currency_list_name:
                if 'USD' in currency_list_name:
                    if prorate_obj.global_currency_rate <= 1.0:
                        raise osv.except_osv(_('Error!'), _('En Moneda Extranjera la Divisa debe ser Superior a 1.0'))

            valuation_account_id = ir_values.get_default(cr, uid, 'stock.prorate', 
                                    'valuation_account_id', company_id=prorate_obj.company_id.id)
            if not valuation_account_id:
                if prorate_obj.valuation_account_id:
                    valuation_account_id = prorate_obj.valuation_account_id.id
                else:
                    raise osv.except_osv(_('Error Configuracion!'),_('Necesitas configurar la Cuenta de Evaluacion para la Compañia.\nConsulta al Administrador.'))
            partial_move_data = []
            total_representation = 0.0

            # cr.dictfetchall()
            # cr.execute("""
            #     select 
            #     spl.product_id,
            #     spl.sent_qty as quantity,
            #     spl.sent_uom_id as product_uom,
            #     spl.prodlot_id,
            #     spl.move_id,
            #     sm.location_id,
            #     sm.location_dest_id,
            #     spl.sent_qty as update_cost,
            #     spl.total_incl_prorate / spl.sent_qty as cost,
            #     spl.currency_id as currency
            #     from stock_prorate_stock_line as spl
            #     join stock_move as sm on spl.move_id = sm.id
            #     and spl.prorate_id = %s
            #     """ % prorate_obj.id)
            # cr_res = cr.dictfetchall()

            for stockable_line in prorate_obj.stock_prorate_ids:
                if stockable_line.product_id.track_incoming and not stockable_line.prodlot_id:
                    raise osv.except_osv(_('Numero de serie no especificado.'),_('Asigna un numero de Serie al Producto. %s.'%(stockable_line.product_id.name)))
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
                ############### VALIDACION CHERMAN #####################
                if stockable_line.move_id.picking_id.state == 'cancel':
                    raise osv.except_osv(_('Error de Validacion'), _(
                        'El Albaran %s de la Compra %s se encuentra en estado Cancelado, por lo cual no se puede Validar el Prorateo, elimine la linea o Recarge las Compras!' % (stockable_line.move_id.picking_id.name, stockable_line.purchase_id.name,)))
                ###################### FIN ##############################
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
                    raise osv.except_osv(_('Error !'),
                        _('Cuenta de Gastos no definica para el Producto: %s') % \
                            (po_line.product_id.name,))
                move_line = (0,0, {
                    'name': _('Reclasificacion de los Gastos: ') + service_line.purchase_id.name + ' - ' + po_line.name,
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
                        'name': _('Reclasificacion de los Gastos: ') + prorate_obj.name,
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

    def valida_stocks(self, cr, uid, ids, context=None):

        for rec in self.browse(cr, uid, ids, context=None):
            for line in rec.stock_prorate_ids:
                if line.move_id.picking_id.state == 'cancel':
                    raise osv.except_osv(_('Error de Validacion'), _(
                        'El Albaran %s de la Compra %s se encuentra en estado Cancelado, por lo cual no se puede Validar el Prorateo, elimine la linea o Recarge las Compras!' % (line.move_id.picking_id.name, line.purchase_id.name,)))
        return True

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
            currency_parent_id = prorate.currency_id.id
            if prorate.update_currency_rate:
                currency_flag =True
                cr.execute("""
                    select currency_id from stock_prorate_service_line
                    where prorate_id = %s group by currency_id
                    """ % prorate.id )
                cr_res = cr.fetchall()
                currency_list = [x[0] for x in cr_res if x]
                for currency in currency_list:
                    if currency != currency_parent_id:
                        cr.execute("""
                            select sum(%s*total) from stock_prorate_service_line
                            where currency_id = %s and prorate_id = %s
                            """,(prorate.global_currency_rate, currency, prorate.id))
                        cr_res = cr.fetchall()
                        total_expense = cr_res[0][0] if cr_res else 0.0

                        cr.execute("""
                            update stock_prorate_service_line
                            set total_in_company_currency = %s * total,
                            currency_rate = %s
                            where currency_id = %s and prorate_id = %s
                            """,(prorate.global_currency_rate, 
                                prorate.global_currency_rate, currency, prorate.id))
                    else:
                        cr.execute("""
                            select id from stock_prorate_service_line
                            where currency_id = %s and prorate_id = %s
                            and total_in_company_currency > 0.0
                            """, (currency, prorate.id, ))
                        cr_res = cr.fetchall()
                        prorate_service_list1 = [x[0] for x in cr_res if x]

                        if prorate_service_list1:
                            cr.execute("""
                            select sum(total_in_company_currency)
                            from stock_prorate_service_line where id in %s
                            """, (tuple(prorate_service_list1),))
                        cr_res = cr.fetchall()
                        total_expense_add1 = cr_res[0][0] if cr_res else 0.0
                        total_expense = total_expense+total_expense_add1

                        cr.execute("""
                            select id from stock_prorate_service_line
                            where currency_id = %s and prorate_id = %s
                            and total_in_company_currency <= 0.0
                            """, (currency, prorate.id, ))
                        cr_res = cr.fetchall()
                        prorate_service_list2 = [x[0] for x in cr_res if x]

                        if prorate_service_list2:
                            cr.execute("""
                            select sum(total_in_company_currency)
                            from stock_prorate_service_line where id in %s
                            """, (tuple(prorate_service_list2),))
                        cr_res = cr.fetchall()
                        total_expense_add2 = cr_res[0][0] if cr_res else 0.0
                        total_expense = total_expense+total_expense_add2

                # for service_prorate in prorate.service_prorate_ids:
                #     if service_prorate.currency_id.id != currency_parent_id:
                #         total_in_company_currency = prorate.global_currency_rate * service_prorate.total
                #         service_prorate.write({
                #             'currency_rate':prorate.global_currency_rate,
                #             'total_in_company_currency':total_in_company_currency
                #         })
                #         total_expense += total_in_company_currency
                #         service_prorate.refresh()
                #     else:
                #         if service_prorate.total_in_company_currency:
                #             total_expense += service_prorate.total_in_company_currency
                #         else:
                #             total_expense += service_prorate.total

                #         service_prorate.refresh()
                currency_list = []
                cr.execute("""
                    select currency_id from stock_prorate_stock_line
                    where prorate_id = %s group by currency_id
                    """ % prorate.id )
                cr_res = cr.fetchall()
                currency_list = [x[0] for x in cr_res if x]
                for currency in currency_list:
                    if currency != currency_parent_id:
                        cr.execute("""
                            select sum(%s*price_unit*sent_qty) from stock_prorate_stock_line
                            where currency_id = %s and prorate_id = %s
                            """,(prorate.global_currency_rate, currency, prorate.id))
                        cr_res = cr.fetchall()
                        total_stockable_amount = cr_res[0][0] if cr_res else 0.0

                        cr.execute("""
                            update stock_prorate_stock_line
                            set total_in_company_currency = %s * total,
                            currency_rate = %s, sent_total = %s * price_unit * sent_qty
                            where currency_id = %s and prorate_id = %s
                            """,(prorate.global_currency_rate, 
                                prorate.global_currency_rate,
                                prorate.global_currency_rate,
                                currency, prorate.id))

                    else:
                        cr.execute("""
                            select id from stock_prorate_stock_line
                            where currency_id = %s and prorate_id = %s
                            and sent_total > 0.0
                            """, (currency, prorate.id, ))
                        cr_res = cr.fetchall()
                        prorate_stock_list1 = [x[0] for x in cr_res if x]

                        if prorate_stock_list1:
                            cr.execute("""
                            select sum(sent_total)
                            from stock_prorate_stock_line where id in %s
                            """, (tuple(prorate_stock_list1),))
                        cr_res = cr.fetchall()
                        total_stockable_amount_add1 = cr_res[0][0] if cr_res else 0.0
                        total_stockable_amount = total_stockable_amount+total_stockable_amount_add1

                        cr.execute("""
                            select id from stock_prorate_stock_line
                            where currency_id = %s and prorate_id = %s
                            and sent_total <= 0.0
                            """, (currency, prorate.id, ))
                        cr_res = cr.fetchall()
                        prorate_stock_list2 = [x[0] for x in cr_res if x]

                        if prorate_stock_list2:
                            cr.execute("""
                            select sum(sent_total)
                            from stock_prorate_stock_line where id in %s
                            """, (tuple(prorate_stock_list2),))
                        cr_res = cr.fetchall()
                        total_stockable_amount_add2 = cr_res[0][0] if cr_res else 0.0
                        total_stockable_amount = total_stockable_amount+total_stockable_amount_add2

                # for stock_prorate in prorate.stock_prorate_ids:
                #     if stock_prorate.currency_id.id != currency_parent_id:
                #         sent_total = prorate.global_currency_rate * stock_prorate.price_unit * stock_prorate.sent_qty
                #         stock_prorate.write({
                #             'currency_rate':prorate.global_currency_rate,
                #             'total_in_company_currency':prorate.global_currency_rate * stock_prorate.total,
                #             'sent_total': sent_total
                #         })
                #         total_stockable_amount += sent_total
                #         stock_prorate.refresh()
                #     else:
                #         if stock_prorate.sent_total:
                #             total_stockable_amount += stock_prorate.sent_total
                #             stock_prorate.refresh()
                #         else:
                #             total_stockable_amount += stock_prorate.price_unit * stock_prorate.sent_qty
                #             stock_prorate.refresh()
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
                
                # if 'sent_total' in res:
                #     representation = (res['sent_total']/prorate.total_stockable_amount)*100.0
                #     res.update(stockable_prorate_pool.onchange_representation(cr, uid, [],
                #             stock_prorate.product_id.id,stock_prorate.uom_id.id,stock_prorate.sent_uom_id.id,
                #             stock_prorate.sent_qty,stock_prorate.price_unit,prorate.total_expense,stock_prorate.sent_total,
                #             representation,stock_currency_id,prorate_currency_id, context)['value'])
                #     res.update({'representation_percent':representation})
                # stock_prorate.write(res)
            prorate.write({'update_needed':False,'update_currency_rate':False})
            ######### CHERMAN  ##########
            prorate.refresh_lines()
        return True

    ########### CODIGO CHERMAN ###############
    def refresh_lines(self, cr, uid, ids, context=None):
        ##### ELIMINANDO LINEAS CON CANTIDAD A ENVIAR EN 0 #########
        prorate_stock = self.pool.get('stock.prorate.stock.line')
        prorate_stock_ids = prorate_stock.search(cr, uid, [('prorate_id','=',ids[0]),('sent_qty','<=',0)])
        prorate_stock.unlink(cr, uid, prorate_stock_ids, context=None)
        ######### COMIENZAN LOS CALCULOS ###########
        for rec in self.browse(cr, uid, ids, context=None):
            global_currency_rate = rec.global_currency_rate
            amount_total_services = 0.0
            representation_amount = 0.0
            cr.execute("""
                select sum(total_in_company_currency) from stock_prorate_service_line
                where prorate_id = %s ;
                """ % rec.id)
            cr_res = cr.fetchall()
            amount_total_services = cr_res[0][0] if cr_res else 0.0
            # for service in rec.service_prorate_ids:
            #     amount_total_services+= service.total_in_company_currency
            cr.execute("""
                select sum((price_unit*sent_qty)*currency_rate) 
                from stock_prorate_stock_line
                where prorate_id = %s ;
                """ % rec.id)
            cr_res = cr.fetchall()
            representation_amount = cr_res[0][0] if cr_res else 0.0
            # for stock_ac in rec.stock_prorate_ids:
            #     currency_rate = stock_ac.currency_rate
            #     price_unit = stock_ac.price_unit
            #     sent_qty = stock_ac.sent_qty
            #     representation_amount += (price_unit*sent_qty)*currency_rate
            for stock in rec.stock_prorate_ids:
                # total_incl_prorate = stock.total_incl_prorate
                amount_extra_services = stock.amount_extra_services

                currency_rate = stock.currency_rate
                new_price_unit = 0.0
                price_unit = stock.price_unit
                sent_qty = stock.sent_qty
                amount_subtotal = price_unit*sent_qty
                amount_subtotal_currency = currency_rate*amount_subtotal
                # prorated_expense = stock.prorated_expense
                try:
                    representation = amount_subtotal_currency/representation_amount
                except:
                    representation = 0.0
                try:
                    total_service = representation * amount_total_services
                except:
                    total_service = 0.0
                amount_subtotal_qty = (price_unit*stock.qty)*currency_rate
                total_incl_prorate = amount_subtotal_currency+total_service+amount_extra_services
                if total_incl_prorate > 0.0 and sent_qty > 0.0:
                    new_price_unit = float(total_incl_prorate)/float(sent_qty)
                    stock.write({'new_price_unit':new_price_unit,
                        'total_in_company_currency': amount_subtotal_qty,
                        'sent_total': amount_subtotal_currency,
                        'total_incl_prorate': total_incl_prorate,
                        'prorated_expense': total_service,
                        'representation_percent': representation*100,
                        })

        return True

    ##################### FIN ###################

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
                self_br = self.browse(cr, uid, ids[0], context=None)

                ######## AGREGAMOS ESTAS LINEAS ARGIL CONSULTING ######
                if service_dict['currency_id'] != self_br.currency_id.id:
                    service_lines.append(service_dict)
                    total_services += price_total_company_curr
                else:
                    total = service_dict['total']
                    service_dict.update({'currency_rate':1,'total_in_company_currency':total})
                    service_lines.append(service_dict)
                    total_services += total
                ################## FIN #####################
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
            try:
                representation = (stockable_line['sent_total']/total_stockable_amount)
            except:
                representation = 0.0
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
            
            #### MODIFICAR ESTA PARTE PARA VALIDAR EL ERROR ##### *** ERROR ***
            try:
                new_price_unit = ((amount_unit * avail_qty) + (new_amount))/(avail_qty + qty)
            except:
                new_price_unit = 0.0
            stockable_line.update({
                'representation_percent': representation*100.0,
                'prorated_expense': prorated_expense,
                'total_incl_prorate': total_incl_prorate,
                'new_price_unit': new_price_unit})
        return total_services,total_stockable_amount, service_lines,stockable_lines
       
# #         for prorate in self.browse(cr ,uid, ids, context):
#             for stock_prorate in prorate.stock_prorate_ids:
#                 if not stock_prorate.sent_total:
#                     continue
                
#                 prorate_currency_id = prorate.currency_id.id
#                 stock_currency_id = stock_prorate.currency_id.id
#                 currency_rate = prorate.global_currency_rate
#                 prorate_expense = stock_prorate.prorated_expense

#                 if currency_flag:
#                     currency_rate = prorate.global_currency_rate
#                     prorate_currency_id = False
#                     stock_currency_id = False
#                 res = stockable_prorate_pool.onchange_sent_qty(cr, uid, [], 
#                                 stock_prorate.price_unit, stock_prorate.sent_qty,
#                                 stock_currency_id,prorate_currency_id,stock_prorate.date_planned,currency_rate)['value']
                
#                 representation = (res['sent_total']/prorate.total_stockable_amount)*100.0
                
#                 ##### AGREGADO CHERMAN #######
#                 cr.execute("select sum(total_in_company_currency) from stock_prorate_service_line where prorate_id = %s" % prorate.id)
#                 amount_prorate = cr.fetchall()
#                 if amount_prorate[0][0] != None:
#                     amount_prorate = amount_prorate[0][0]
#                 else:
#                     amount_prorate = 0.0

#                 amount_global_currency = amount_prorate*(representation/100.0)
                
#                 global_currency_rate = prorate.global_currency_rate
#                 sent_total = stock_prorate.sent_total
#                 total_stockable_amount = prorate.total_stockable_amount
#                 sent_qty = stock_prorate.sent_qty

#                 new_total_prorate = amount_global_currency + total_stockable_amount
#                 new_price_unit = new_total_prorate/sent_qty

#                 res.update({'sent_total': sent_total, 
#                             'prorated_expense': amount_global_currency, 
#                             'total_incl_prorate': new_total_prorate, 
#                             'new_price_unit': new_price_unit}
#                             )
#                 # res.update(stockable_prorate_pool.onchange_representation(cr, uid, [],
#                 #         stock_prorate.product_id.id,stock_prorate.uom_id.id,stock_prorate.sent_uom_id.id,
#                 #         stock_prorate.sent_qty,stock_prorate.price_unit,prorate.total_expense,stock_prorate.sent_total,
#                 #         representation,stock_currency_id,prorate_currency_id, context)['value'])
#                 ##### TERMINA #######

#                 res.update({'representation_percent':representation})
#                 stock_prorate.write(res)
#             prorate.write({'update_needed':False,'update_currency_rate':False})
#         return True
    

stock_prorate()

class stock_prorate_stock_line(osv.osv):
    _name = 'stock.prorate.stock.line'
    _inherit ='stock.prorate.stock.line'
    _columns = {
        'pedimento_id': fields.many2one('stock.production.lot.pedimento','Pedimento', ondelete="cascade"),
        'amount_extra_services': fields.float('Prorateo Servicios Extra', digits=(14,4), readonly=True),
        }

    _defaults = {
        }


    def onchange_sent_qty(self,cr, uid, ids, price_unit,sent_qty,from_currency,
                          to_currency,date,currency_rate=1.0, context=None):
        #added currency rate so that if any of the currency is not specified, 
        #then this currency rate will be considered, mainly useful in update purchase order function update_stockable_lines
        
        ###### CHERMAN CODE ########
        res = {}
        prorated_expense = 0.0
        representation_percent = 0.0
        total_incl_prorate = 0.0
        for rec in self.browse(cr, uid, ids, context=None):
            prorated_expense = rec.prorated_expense
            representation_percent = rec.representation_percent
        if sent_qty > 0.0:
            total_in_company_currency = sent_qty * price_unit * currency_rate
            sent_total = sent_qty * price_unit * currency_rate
            total_incl_prorate = prorated_expense + sent_total
            new_price_unit = total_incl_prorate/sent_qty
            res.update({
                'prorated_expense': prorated_expense,
                'representation_percent': representation_percent,
                'total_in_company_currency': total_in_company_currency,
                'sent_total': sent_total,
                'total_incl_prorate': total_incl_prorate,
                'new_price_unit': new_price_unit,
                })
        return {'value':res}
        ####### FIN CHERMAN
        # result = {'value':{}}
        # ctx = {}
        # ctx['date'] = date or False
        # currency_pool = self.pool.get('res.currency')
        # if from_currency != to_currency:
        #     price_unit_company_curr = currency_pool.compute(cr, uid, from_currency,
        #                                     to_currency, price_unit, context=ctx)
        #     sent_total = price_unit_company_curr * sent_qty
        # else:
        #     sent_total = price_unit * sent_qty * currency_rate
        # result['value'].update({'sent_total': sent_total})
        # if not sent_qty:
        #     return result #TODO add warning if no sent qty 
        # return result
    

    def copy(self, cr, uid, id, default=None, context=None):
        # ref = self.pool.get('ir.sequence').get(cr, uid, 'pre.order.tpv')
        if not default:
            default = {}
        default.update({
                        
                        'pedimento_id': False,
                        })
        return super(stock_prorate_stock_line, self).copy(cr, uid, id, default, context=context)

stock_prorate_stock_line()


#### ASISTENTE DE ASIGNACION DE PEDIMENTOS

class wizard_prorate_pedimento(osv.osv_memory):
    _name = 'wizard.prorate.pedimento'
    _description = 'Pedimentos para Prorateo'
    _columns = {
    'line_ids': fields.one2many('wizard.prorate.pedimento.line','wizard_id', 'Productos/Pedimentos'),
    'pedimento_id': fields.many2one('pedimento.custom','Pedimento de Compra'),
    'load_lines': fields.boolean('Cargar Lineas'),
    'active_prorate': fields.integer('Active ID'),
    }

    def _get_active(self, cr, uid, context=None):
        active_ids = context.get('active_ids', False)
        if active_ids:
            active_ids = active_ids[0]
        return active_ids

    _defaults = { 
    'load_lines': True,
    'active_prorate': _get_active,
        }
    def on_change_lines(self, cr, uid, ids, load_lines, pedimento_id, active_prorate,  context=None):
        res = {}
        lines = []
        prorate_obj = self.pool.get('stock.prorate')

        if pedimento_id:

            pedimento_obj = self.pool.get('pedimento.custom')
            pedimento_br = pedimento_obj.browse(cr, uid, pedimento_id, context=None)
            no_serie = pedimento_br.pedimento_sequence
            stock_lot_obj = self.pool.get('stock.production.lot.pedimento')
            
            for prorate in prorate_obj.browse(cr, uid, [active_prorate], context=None):
                
                for product in prorate.stock_prorate_ids:
                    vals = {'name':no_serie,'product_id':product.product_id.id,'stock_available':0.0,'pedimento_id':pedimento_id}
                    stock_lot_id = stock_lot_obj.search(cr, uid, [('name','=',no_serie),('product_id','=',product.product_id.id)])
                    stock_lot_id = stock_lot_id[0] if stock_lot_id else False
                    if not stock_lot_id:
                        stock_lot_id = stock_lot_obj.create(cr, uid, vals, context=None)
                    xline = (0,0,{
                        'product_id': product.product_id.id,
                        'pedimento_id': stock_lot_id,
                        'qty': product.sent_qty,
                        'stock_prorate_line': product.id,
                        })
                    lines.append(xline)
        else:
            for prorate in prorate_obj.browse(cr, uid, [active_prorate], context=None):
                for product in prorate.stock_prorate_ids:
                    xline = (0,0,{
                        'product_id': product.product_id.id,
                        'pedimento_id': False,
                        'qty': product.sent_qty,
                        'stock_prorate_line': product.id,
                        })
                    lines.append(xline)
        res['line_ids'] = [x for x in lines]
        return {'value':res}

    def assign_pedimentos(self, cr, uid, ids, context=None):
        active_ids = context and context.get('active_ids', False)
        prorate_obj = self.pool.get('stock.prorate')
        for rec in self.browse(cr, uid, ids, context=None):
            prorate_obj.write(cr, uid, active_ids, {'update_needed':True})
            for line in rec.line_ids:
                if line.pedimento_id:
                    stock_available = line.pedimento_id.stock_available
                    if line.stock_prorate_line.pedimento_id:
                        if line.stock_prorate_line.pedimento_id.id != line.pedimento_id.id:
                            qty_stock = line.stock_prorate_line.sent_qty
                            qty_pedimento = line.stock_prorate_line.pedimento_id.stock_available
                            qty_total = qty_pedimento - qty_stock

                            line.stock_prorate_line.pedimento_id.write({'stock_available': qty_total})

                            line.stock_prorate_line.move_id.write({'pedimento_id':line.pedimento_id.id})
                            line.stock_prorate_line.write({'pedimento_id':line.pedimento_id.id})
                            line.stock_prorate_line.prorate_id.write({'pedimento_assign':True,'global_currency_rate':line.pedimento_id.pedimento_id.type_change if line.pedimento_id.pedimento_id.type_change > 0 else 1})
                            stock_available = line.pedimento_id.stock_available + line.qty
                            line.pedimento_id.write({'stock_available':stock_available})
                        else:
                            qty_stock = line.stock_prorate_line.sent_qty
                            qty_pedimento = line.pedimento_id.stock_available
                            qty_total = qty_pedimento - qty_stock

                            line.stock_prorate_line.move_id.write({'pedimento_id':line.pedimento_id.id})
                            line.stock_prorate_line.write({'pedimento_id':line.pedimento_id.id})
                            line.stock_prorate_line.prorate_id.write({'pedimento_assign':True,'global_currency_rate':line.pedimento_id.pedimento_id.type_change if line.pedimento_id.pedimento_id.type_change > 0 else 1})
                            stock_available = qty_total + line.qty
                            line.pedimento_id.write({'stock_available':stock_available})
                    else:
                        line.stock_prorate_line.move_id.write({'pedimento_id':line.pedimento_id.id})
                        line.stock_prorate_line.write({'pedimento_id':line.pedimento_id.id})
                        line.stock_prorate_line.prorate_id.write({'pedimento_assign':True,'global_currency_rate':line.pedimento_id.pedimento_id.type_change if line.pedimento_id.pedimento_id.type_change > 0 else 1})
                        stock_available = line.pedimento_id.stock_available + line.qty
                        line.pedimento_id.write({'stock_available':stock_available})
            #         line.stock_prorate_line.move_id.write({'pedimento_id': line.pedimento_id.id})
            #         if line.stock_prorate_line.prorate_id.currency_id.id != line.stock_prorate_line.currency_id.id :
            #             line.stock_prorate_line.write({'currency_rate':line.pedimento_id.pedimento_id.type_change if line.pedimento_id.pedimento_id.type_change > 0 else 1.0})
            # prorate_obj.update_stockable_lines(cr, uid, active_ids, context=None)
        stockable_prorate_pool = self.pool.get("stock.prorate.stock.line")

        for prorate in prorate_obj.browse(cr ,uid, active_ids, context):

            total_expense = 0.0
            total_stockable_amount = 0.0
            currency_flag = False
            currency_flag =True
            total_in_company_currency = 0.0
            for service_prorate in prorate.service_prorate_ids:
                if service_prorate.currency_id.id != prorate.currency_id.id:
                    total_in_company_currency = prorate.global_currency_rate * service_prorate.total
                    service_prorate.write({
                        'currency_rate':prorate.global_currency_rate,
                        'total_in_company_currency':total_in_company_currency
                    })
                    total_expense += service_prorate.total_in_company_currency
                    service_prorate.refresh()
                else:
                    total_expense += total_in_company_currency
                    service_prorate.refresh()
            for stock_prorate in prorate.stock_prorate_ids:
                if stock_prorate.currency_id.id != prorate.currency_id.id:
                    sent_total = prorate.global_currency_rate * stock_prorate.price_unit * stock_prorate.sent_qty
                    stock_prorate.write({
                        'currency_rate':prorate.global_currency_rate,
                        'total_in_company_currency':prorate.global_currency_rate * stock_prorate.total,
                        'sent_total': sent_total
                    })
                    total_stockable_amount += sent_total
                    stock_prorate.refresh()
                else:
                    total_stockable_amount += stock_prorate.sent_total
                    stock_prorate.refresh()
            prorate.write({'total_stockable_amount':total_stockable_amount,'total_expense':total_expense})
            prorate.refresh()
                
#         for prorate in self.browse(cr ,uid, ids, context):
            for stock_prorate in prorate.stock_prorate_ids:
                if not stock_prorate.sent_total:
                    continue
                
                prorate_currency_id = prorate.currency_id.id
                stock_currency_id = stock_prorate.currency_id.id
                currency_rate = prorate.global_currency_rate
                prorate_expense = stock_prorate.prorated_expense

                if currency_flag:
                    currency_rate = prorate.global_currency_rate
                    prorate_currency_id = False
                    stock_currency_id = False
                res = stockable_prorate_pool.onchange_sent_qty(cr, uid, [], 
                                stock_prorate.price_unit, stock_prorate.sent_qty,
                                stock_currency_id,prorate_currency_id,stock_prorate.date_planned,currency_rate)['value']
                
                representation = stock_prorate.representation_percent
                
                ##### AGREGADO CHERMAN #######
                cr.execute("select sum(total_in_company_currency) from stock_prorate_service_line where prorate_id = %s" % prorate.id)
                amount_prorate = cr.fetchall()
                if amount_prorate[0][0] != None:
                    amount_prorate = amount_prorate[0][0]
                else:
                    amount_prorate = 0.0

                amount_global_currency = amount_prorate*(representation/100.0)
                
                global_currency_rate = prorate.global_currency_rate
                sent_total = stock_prorate.sent_total
                total_stockable_amount = prorate.total_stockable_amount
                sent_qty = stock_prorate.sent_qty

                new_total_prorate = amount_global_currency + stock_prorate.total_in_company_currency
                new_price_unit = new_total_prorate/sent_qty

                res.update({'sent_total': sent_total, 
                            'prorated_expense': amount_global_currency, 
                            'total_incl_prorate': new_total_prorate, 
                            'new_price_unit': new_price_unit}
                            )
                # res.update(stockable_prorate_pool.onchange_representation(cr, uid, [],
                #         stock_prorate.product_id.id,stock_prorate.uom_id.id,stock_prorate.sent_uom_id.id,
                #         stock_prorate.sent_qty,stock_prorate.price_unit,prorate.total_expense,stock_prorate.sent_total,
                #         representation,stock_currency_id,prorate_currency_id, context)['value'])
                ##### TERMINA #######

                res.update({'representation_percent':representation})
                stock_prorate.write(res)
            prorate.write({'update_needed':False,'update_currency_rate':False})            
        return True
wizard_prorate_pedimento()

class wizard_prorate_pedimento_line(osv.osv_memory):
    _name = 'wizard.prorate.pedimento.line'
    _description = 'Pedimentos para Prorateo en Productos'
    _columns = {
    'wizard_id': fields.many2one('wizard.prorate.pedimento', 'Ref Asistente'),
    'product_id': fields.many2one('product.product', 'Producto', required=True),
    'pedimento_id': fields.many2one('stock.production.lot.pedimento', 'Pedimento',ondelete='cascade'),
    'qty': fields.integer('Cantidad'),
    'stock_prorate_line': fields.many2one('stock.prorate.stock.line','Linea de Stock Prorate'),
    }
    _defaults = {  

        }
wizard_prorate_pedimento_line()

class stock_prorate(osv.osv):
    _name = 'stock.prorate'
    _inherit ='stock.prorate'
    _columns = {
    'pedimento_assign': fields.boolean('Pedimentos Asignados', help='Esta casilla si es desactivada podemos Asignar Nuevamente los Pedimentos en el Prorateo'),
        }

    _defaults = {
        }
        
stock_prorate()