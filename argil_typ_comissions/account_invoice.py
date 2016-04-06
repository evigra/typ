# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp.osv import osv, fields
import time
# import dateutil
# import dateutil.parser
# from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from openerp import _
# from tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
import openerp.addons.decimal_precision as dp
# import netsvc
# import openerp
# import calendar
# import tempfile
# from xml.dom import minidom
# import os
# import base64
# import hashlib
# import tempfile
# import os
# import codecs
from openerp import SUPERUSER_ID
import sys
reload(sys)  
sys.setdefaultencoding('utf8')

AVAILABLE_STATES = [
    ('draft','Borrador'),
    ('proforma','Pro-forma'),
    ('proforma2','Pro-forma'),
    ('open','Abierto'),
    ('paid','Pagado'),
    ('cancel','Cancelado'),
]

AVAILABLE_TYPES = [
    ('out_invoice','Factura Cliente'),
    ('in_invoice','Factura Proveedor'),
    ('out_refund','Nota Credito Cliente'),
    ('in_refund','Nota Credito Proveedor'),
]

class account_invoice(osv.osv):
    _inherit ='account.invoice'

    def _get_date_payment(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            date = False
            if rec.state == 'paid' and rec.residual <= 0.0 and rec.type == "out_invoice" :
                date_last_payments = []                
                ###################  #####################
                for pagos in rec.payment_ids:
                    date_last_payments.append(pagos.date)
                try:
                    date_last_payments_sorted = sorted(date_last_payments)
                    last_payment_date = date_last_payments_sorted[-1]
                    res[rec.id] = last_payment_date
                except:
                    res = {}
            elif rec.state == 'open' and rec.residual <= 0.0 and rec.type == "out_invoice" :
                date_last_payments = []                
                ###################  #####################
                for pagos in rec.payment_ids:
                    date_last_payments.append(pagos.date)
                try:
                    date_last_payments_sorted = sorted(date_last_payments)
                    last_payment_date = date_last_payments_sorted[-1]
                    res[rec.id] = last_payment_date
                except:
                    res = {}
        return res

    def _get_date_payment_period(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            date = False
            if rec.state == 'paid' or rec.residual <= 0.0 and rec.type == "out_invoice" :
                date_last_payments = []                
                ###################  #####################
                for pagos in rec.payment_ids:
                    date_last_payments.append(pagos.date)
                date_last_payments_sorted = sorted(date_last_payments)
                try:
                    last_payment_date = date_last_payments_sorted[-1]
                    split_date = last_payment_date.split('-')
                    res[rec.id] = split_date[1]+'/'+split_date[0]
                except:
                    res = {}
        return res

    _columns = {
      'user_reasigned_id': fields.many2one('res.users','Comercial Reasignado', help='Esta venta aplicara comision para el Vendedor Reasignado', ),
      'reasigned_sale': fields.boolean('Reasignar Venta', help='Permite asignar la Venta a otro Vendedor', ),
      'date_payment_real': fields.function(_get_date_payment,string='Fecha Liquidacion Factura', type="date", help='Fecha en que se liquido o se Pago la Factura', store=True,),
      'period_payment_real': fields.function(_get_date_payment_period,string='Periodo Liquidacion Factura', type="char", size=128, help='Periodo en que se liquido o se Pago la Factura', store=True,),
      'invoice_customer_id': fields.many2one('account.invoice','Factura Cliente'),
      'invoice_customer_refund_id': fields.many2one('account.invoice','Nota Credito', readonly=True),
      'rel_invoice': fields.boolean('Relacionada Factura Cliente', help='Indica que esta Nota de Credito esta relacionada con una Factura de Cliente'),

      }

    _defaults = {  
        }

    def write(self, cr, uid, ids, vals, context=None):
        if 'user_reasigned_id' in vals:
            user_reasigned_id = vals['user_reasigned_id']
            user_br = self.pool.get('res.users').browse(cr, uid, user_reasigned_id, context=None)
            uid_br = self.pool.get('res.users').browse(cr, uid, uid, context=None)
            self.message_post(cr, uid, ids, body=_("La Comision fue Reasignada al Vendedor <b><em>%s</em></b> por el Usuario <b><em>%s</em></b> ." % (user_br.name, uid_br.name)) ,context=context)

        # elif 'invoice_customer_id' in vals:
        #     invoice_customer_id = vals['invoice_customer_id']
        #     cr.execute("update account_invoice set invoice_customer_refund_id = %s where id=%s" % (ids[0],invoice_customer_id,))

        res = super(account_invoice, self).write(cr, uid, ids, vals, context=None)
        return res

    ####### NOTA TODOS LOS MARGENES ESTAN EXPRESADOS EN LA MONEDA DE LA FACTURA MXN O USD ##########
    def invoice_validate(self, cr, uid, ids, context=None):
        result =  super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.move_id and rec.type == 'out_invoice':
                move_id = rec.move_id.id
                currency_id = rec.currency_id.id
                currency_base = rec.company_id.currency_id.id
                for line in rec.invoice_line:
                    quantity = line.quantity
                    product_id = line.product_id.id
                    if line.price_unit > 0.0:
                        if currency_id == currency_base:
                            if product_id and line.price_unit > 0.0:
                                price_cost = 0.0
                                if line.product_id.pack_line_ids:
                                    qty_line = line.quantity
                                    for nan_prod in line.product_id.pack_line_ids:
                                        nan_prod_qty = qty_line * nan_prod.quantity
                                        nan_prod_id = nan_prod.product_id.id
                                        cr.execute("select debit from account_move_line where product_id=%s and quantity=%s and move_id=%s and debit>0.0" ,(nan_prod_id,nan_prod_qty,rec.move_id.id,))
                                        nan_price_cost = cr.fetchall()
                                        try:
                                            nan_price_cost = nan_price_cost[0][0] if nan_price_cost[0][0] != None else 0.0
                                        except:
                                            nan_price_cost = 0.0
                                        price_cost += nan_price_cost
                                else:
                                    cr.execute("select debit from account_move_line where product_id=%s and quantity=%s and move_id=%s and debit>0.0" %(product_id,quantity,rec.move_id.id,))
                                    price_cost = cr.fetchall()
                                    try:
                                        price_cost = price_cost[0][0] if price_cost[0][0] != None else 0.0
                                    except:
                                        price_cost = 0.0
                                margin_percentage = 0.0
                                margin_amount = 0.0
                                currency_tc = 1.0
                                #subtotal_line = line.price_unit * line.quantity
                                subtotal_line = line.price_subtotal
                                subtotal_cost = price_cost
                                                    
                                margin_amount = subtotal_line - subtotal_cost
                                
                                if margin_amount > 0.0 and subtotal_cost > 0.0:
                                    # margin_percentage = (margin_amount/subtotal_cost)*100
                                    margin_percentage = (margin_amount/subtotal_line)*100
                                line.write({
                                            'margin_amount': margin_amount,
                                            'margin_percentage': margin_percentage,
                                            'currency_tc': 1,
                                            'price_cost': price_cost,
                                            })
                        else:
                            if product_id and line.price_unit > 0.0:
                                price_cost = 0.0
                                if line.product_id.pack_line_ids:
                                    qty_line = line.quantity
                                    for nan_prod in line.product_id.pack_line_ids:
                                        nan_prod_qty = qty_line * nan_prod.quantity
                                        nan_prod_id = nan_prod.product_id.id
                                        cr.execute("select amount_currency from account_move_line where product_id=%s and quantity=%s and move_id=%s and debit>0.0" ,(nan_prod_id,nan_prod_qty,rec.move_id.id,))
                                        nan_price_cost = cr.fetchall()
                                        try:
                                            nan_price_cost = nan_price_cost[0][0] if nan_price_cost[0][0] != None else 0.0
                                        except:
                                            nan_price_cost = 0.0
                                        price_cost += nan_price_cost
                                else:
                                    cr.execute("select amount_currency from account_move_line where product_id=%s and quantity=%s and move_id=%s and debit>0.0" %(product_id,quantity,rec.move_id.id,))
                                    price_cost = cr.fetchall()
                                    try:
                                        price_cost = price_cost[0][0] if price_cost[0][0] != None else 0.0
                                    except:
                                        price_cost = 0.0
                            margin_percentage = 0.0
                            margin_amount = 0.0
                            currency_tc = 1.0
                            ### Tomando los Valores cuando la moneda es distinta
                            subtotal_line = line.price_subtotal
                            #subtotal_line = line.price_unit * line.quantity
                            subtotal_cost = price_cost
                            cr.execute("select rate from res_currency_rate where currency_id=%s and name<= %s order by name desc limit 1", (currency_id, rec.date_invoice,))
                            currency_tc = cr.fetchall()
                            try:
                                currency_tc = currency_tc[0][0] if currency_tc[0][0] != None else 1.0
                            except:
                                currency_tc = 1.0
                            #subtotal_cost = subtotal_cost*currency_tc
                            margin_amount = subtotal_line - subtotal_cost

                            if margin_amount > 0.0 and subtotal_cost > 0.0:
                                #margin_percentage = (margin_amount/subtotal_cost)*100
                                margin_percentage = (margin_amount/subtotal_line)*100
                            line.write({
                                        'margin_amount': margin_amount,
                                        'margin_percentage': margin_percentage,
                                        'currency_tc': currency_tc,
                                        'price_cost': price_cost,
                                        })
                            # raise osv.except_osv(
                            #         _("MODO DEBUG!"), 
                            #         _("<< INTERRUPCION CHERMAN >>")
                            #         )

            elif rec.type == 'out_refund':
                if rec.invoice_customer_id:
                    cr.execute("update account_invoice set invoice_customer_refund_id = %s where id=%s" % (ids[0],rec.invoice_customer_id.id,))
        return result
    
    def action_cancel(self, cr, uid, ids, context=None):
        result = super(account_invoice, self).action_cancel(cr, uid, ids, context)
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.type == 'out_refund':
                if rec.invoice_customer_id:
                    cr.execute("update account_invoice set invoice_customer_refund_id = Null where id=%s" % (rec.invoice_customer_id.id,))
                rec.write({'rel_invoice':False,'invoice_customer_id':False})
        return result
# class account_invoice(osv.osv):
#     _inherit ='account.invoice'
#     _columns = {
#       'refund_account_invoice': fields.many2one('account.invoice','Factura Relacionada', help='Indica la Factura que Se relaciona con esta Nota de Credito'),
#       'not_rel_invoice': fields.boolean('No Relacionada', help='Indica que no necesita relacionarse con una Factura'),
#     }



#     def onchange_partner_id(self, cr, uid, ids, type, partner_id, date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
#         result = super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id, date_invoice, payment_term, partner_bank_id, company_id)
#         partner_b = self.pool.get('res.partner').browse(cr, uid, [partner_id], context=None)[0]
#         user_id = partner_b.user_id.id if partner_b.user_id.id else uid
#         result['value'].update({'user_id' : user_id})
#         return result
# account_invoice()

# class product_category(osv.osv):

#     def name_get(self, cr, uid, ids, context=None):
#         if isinstance(ids, (list, tuple)) and not len(ids):
#             return []
#         if isinstance(ids, (long, int)):
#             ids = [ids]
#         reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
#         res = []
#         for record in reads:
#             name = record['name']
#             if record['parent_id']:
#                 name = record['parent_id'][1]+' / '+name
#             res.append((record['id'], name))
#         return res

#     def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
#         res = self.name_get(cr, uid, ids, context=context)
#         return dict(res)

#     _name = "product.category"
#     _inherit = "product.category"
#     _columns = {
#         'complete_name': fields.function(_name_get_fnc, type="char", string='Name', store=True),
#         }

class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit ='account.invoice.line'

    # def _get_margins(self, cr, uid, ids, field_name, args, context=None):
    #     print "############### EJECUTANDO FUNCION ACTUALIZAR >>>>>>"
    #     res = {
    #         'margin_amount': 0.0,
    #         'margin_percentage': 0.0,
    #         'currency_tc': 1,
    #         }
    #     for rec in self.browse(cr, uid, ids, context=None):
    #         margin_amount = 0.0
    #         margin_percentage = 0.0
    #         price_cost = 0.0
    #         sale_order = self.pool.get('sale.order')
    #         sale_order_line = self.pool.get('sale.order.line')
    #         origin = rec.invoice_id.origin
    #         by_order_line = False
    #         if rec.product_id:
    #             price_cost = rec.product_id.standard_price
    #             #by_order_line = True # True indica que el precio ya se convirtio a Moneda Base
    #         if rec.product_id and price_cost > 0.0:
    #             if rec.invoice_id.type in ('out_invoice','out_refund'):
    #                 currency_id = rec.invoice_id.currency_id.id
    #                 currency_base = rec.invoice_id.company_id.currency_id.id
    #                 if currency_id == currency_base:
    #                     subtotal_line = rec.price_subtotal
    #                     subtotal_cost = price_cost * rec.quantity
                                            
    #                     margin_amount = subtotal_line - subtotal_cost
                        
    #                     if margin_amount > 0.0:
    #                         margin_percentage = (margin_amount/subtotal_line)*100
    #                     res[rec.id] =  {
    #                                     'margin_amount': margin_amount,
    #                                     'margin_percentage': margin_percentage,
    #                                     'currency_tc': 1,
    #                                     'price_cost': price_cost,
    #                                     }
    #                 else:
    #                     ### Si tiene un Pedido Relacionado el Precio de Coste ya esta en la moneda correspondiente
    #                     subtotal_line = rec.price_subtotal
    #                     subtotal_cost = price_cost * rec.quantity
    #                     currency_tc = 1
    #                     if by_order_line == False:
    #                         cr.execute("select rate from res_currency_rate where currency_id=%s and name<= %s order by name desc limit 1", (currency_id, rec.invoice_id.date_invoice,))
    #                         currency_tc = cr.fetchall()
    #                         currency_tc = currency_tc[0][0]

    #                         subtotal_cost = subtotal_cost*currency_tc
    #                     margin_amount = subtotal_line - subtotal_cost

    #                     if margin_amount > 0.0:
    #                         margin_percentage = (margin_amount/subtotal_line)*100
    #                     res[rec.id] =  {
    #                                     'margin_amount': margin_amount,
    #                                     'margin_percentage': margin_percentage,
    #                                     'currency_tc': currency_tc,
    #                                     'price_cost': price_cost,
    #                                     }
    #         else:
    #             res[rec.id] =  {
    #                             'margin_amount': 0.0,
    #                             'margin_percentage': 0.0,
    #                             'currency_tc': 1,
    #                             'price_cost': price_cost,
    #                             }
    #     return res

    # def _get_date_category(self, cr, uid, ids, field_name, args, context=None):
    #     res = {}
    #     for rec in self.browse(cr, SUPERUSER_ID, ids, context=None):
            
    #         if rec.product_id:
               
    #             try:
    #                 category_id = rec.product_id.categ_id.id
    #                 res[rec.id] = category_id
    #             except:
    #                 res = {}
    #     return res

    _columns = {
        'category_product_id': fields.related('product_id','categ_id', type="many2one", relation="product.category", string="Categoria", store=False),
        # 'category_product_id': fields.function(_get_date_category, type="many2one", relation="product.category", string="Categoria", store=True),
        # 'price_cost': fields.function(_get_margins, string="Precio Coste", type="float", digits=(8,2), multi="margin", store=False,),
        # 'margin_amount': fields.function(_get_margins, string="Margen", type="float", digits=(8,2), multi="margin", store=False,),
        # 'margin_percentage': fields.function(_get_margins, string="Margen Porcentaje", type="float", digits=(8,2), multi="margin", store=False,),
        # 'currency_tc': fields.function(_get_margins, string="Tasa de Cambio", type="float", digits=(4,8), multi="margin", store=False,),
        'price_cost': fields.float("Precio Coste", type="float", digits=(8,2)),
        'margin_amount': fields.float("Margen", type="float", digits=(8,2)),
        'margin_percentage': fields.float("Margen Porcentaje", type="float", digits=(8,2)),
        'currency_tc': fields.float("Tasa de Cambio", type="float", digits=(4,8)),
        
        'user_invoice_rel': fields.related('invoice_id','user_id', string="Vendedor", type="many2one", relation="res.users", store=False,),
        'invoice_customer_refund_id': fields.related('invoice_id','invoice_customer_refund_id', string="Nota de Credito", type="many2one", relation="account.invoice", store=False,),
        'user_reasigned_invoice_id': fields.related('invoice_id','user_reasigned_id', string="Vendedor Asignado", type="many2one", relation="res.users", store=False,),
        'date_payment_real_invoice': fields.related('invoice_id','date_payment_real', string="Fecha de Pago", type="date", store=False,),
        'date_invoice': fields.related('invoice_id','date_invoice', string="Fecha de Factura", type="date", store=False,),
        'date_due': fields.related('invoice_id','date_due', string="Fecha de Vencimiento", type="date", store=False,),
        'period_payment_real_invoice': fields.related('invoice_id','period_payment_real', string="Periodo de Pago", type="char", size=128, store=False,),
        'payment_term_partner': fields.related('partner_id','property_payment_term', string="Plazo de Venta", type="many2one", relation="account.payment.term", store=False,),
        'state_invoice': fields.related('invoice_id','state', string="Estado de Factura", type="selection", store=False, selection=AVAILABLE_STATES, ),
        'invoice_type': fields.related('invoice_id','type', string="Tipo Factura", type="selection", store=False, selection=AVAILABLE_TYPES, ),
        }

    _defaults = {
        }
    _order = 'id desc'

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        default.update({
                        'price_cost': 0.0, 
                        'margin_amount': 0.0, 
                        'margin_percentage': 0.0,
                        'currency_tc': 1,
                        })
        return super(account_invoice_line, self).copy(cr, uid, id, default, context)


# class account_invoice(osv.osv):
#     _inherit ='account.invoice'
#     _columns = {
#       'picking_invoice_ids': fields.many2many('stock.picking', 'invoice_picking_rel', 'invoice_id', 'picking_id', 'Stocks Send'),
#       'invoice_from_albaran': fields.boolean('Invoice From Stocks'),
#       'product_shipped': fields.boolean('Product Shipped'),
#       'invoice_remaining_ids': fields.one2many('account.product.send.line', 'send_id', 'Product Remaining by Deliver'),
#         'refund_invoice_id': fields.many2one('account.invoice','Factura Relacionada', help='Indica la Factura que Se relaciona con esta Nota de Credito'),
#     }
    
# account_invoice()

# class account_product_send_line(osv.osv):
#     _name = 'account.product.send.line'
#     _description = 'Lineas del Producto Restante de Albaranes'
#     _rec_name = 'product_id'
#     _columns = {
#       'send_id': fields.many2one('account.invoice', 'ID Retorno'),
#         'product_id': fields.many2one('product.product', 'Producto', domain=[('sale_ok', '=', True)], required=True),
#         'product_uom_qty': fields.float('Cantidad', digits_compute= dp.get_precision('Product UoS'), required=True),
#         'product_uom': fields.many2one('product.uom', 'Unidad de Medida', required=True),
#         }

#     _defaults ={
#         }

# account_product_send_line()

