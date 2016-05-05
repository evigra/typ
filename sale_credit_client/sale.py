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

### HERENCIA A CLIENTES PARA IGNORAR VENCIMIENTO ###
class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit ='res.partner'
    _columns = {
    'overdue_invoice': fields.boolean('Ignorar Facturas Vencidas', help='Si este campo esta Activo, las facturas Vencidas no afectaran si el Cliente aun tiene Credito'),

        }

    _defaults = {
        }
res_partner()

# Agregamos manejar una secuencia por cada tienda para controlar viajes
class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"
    _columns = {
    'exced_credit': fields.boolean('Limite de Credito Excedido'),
    'overdue_invoice': fields.boolean('Ignorar Factura Vencida', help='Si este campo esta Activo, esta Factura no Afectara el Credito del Cliente'),
   # 'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order", domain=[('type','=','sale')], change_default=True),
    'global_discount': fields.float('Descuento Global (%)', digits_compute= dp.get_precision('Account'), required=False),
    'tipo_venta': fields.selection([('credit','Credito'),('cash','Contado')], 'Plazo'),

    }

    _defaults = {
        'tipo_venta': 'cash',
        }
     #### ON CHANGE CREDITO ####

    def on_change_termn(self, cr, uid, ids, payment_term, tipo_venta, context=None):
        res = {}
        warning= {}
        if not tipo_venta:
            return {}
        if tipo_venta == 'cash':
            payment_obj = self.pool.get('account.payment.term')
            if payment_term:
                payment_br = payment_obj.browse(cr, uid, payment_term, context=None)
                if not payment_br.line_ids:
                    return {}
            payment_ids = payment_obj.search(cr, uid,
                [('line_ids','=',False)])
            warning = {
                        'title': 'Error!',
                        'message':'En Ventas de Contado solo podra Utilizar Plazos a 0 Dias.\n Si cree que esto es un Error, Contacta al Administrador.'}
            res.update({'payment_term':payment_ids[0]})
            return {'value':res, 'warning': warning}
        return {'value':res}

    def on_change_credito(self, cr, uid, ids, tipo_venta, partner_id, context=None):
        res = {}
        if not partner_id or not tipo_venta:
            return {'value':{'tipo_venta':'cash'}}
        partner_br = self.pool.get('res.partner').browse(cr, uid, partner_id, context=None)
        if partner_br.is_company == False:
            partner_br = partner_br.parent_id
        if not partner_br.property_payment_term:
            warning = {
                        'title': '%s ' % (partner_br.name,),
                        'message':'No tiene definido Plazo de Pago y solo podras Vender de Contado.\n Asigna Plazo ó Contacta al Administrador'}
            return {'value':{'tipo_venta':'cash'},'warning':warning}
        res.update({'payment_term':partner_br.property_payment_term.id})
        return {'value':res}

    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        if not partner_id:
            return {'value':{}}
        if type != 'out_invoice':
            return super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,\
            date_invoice, payment_term, partner_bank_id, company_id)
        warning = {}
        title = False
        message = False
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=None)
        if partner.is_company == False:
            partner = partner.parent_id
        title =  _("Informacion Financiera de %s :") % partner.name
        this = self.get_current_instance(cr, uid, ids)
        message = " "
        warning = {
                'title': title,
                'message': message,
        }

        credit_exc = 0.0
        if partner.credit == 0:
            credit_exc == 0.0
        elif partner.credit > 0.0:
            credit_exc = partner.credit_limit - partner.credit
            if credit_exc < 0.0:
                credit_exc = credit_exc * (-1)

        account_voucher_obj = self.pool.get('account.voucher')
        account_voucher_ids = account_voucher_obj.search(cr, uid, [('partner_id','=',partner_id)])
        date = ''
        for voucher in account_voucher_obj.browse(cr, uid, account_voucher_ids, context=None):
            if voucher.date > date:
                date = voucher.date
        if not account_voucher_ids:
            date = 'No se ah detectado Pago'
        result =  super(account_invoice, self).onchange_partner_id(cr, uid, ids, type, partner_id,\
            date_invoice, payment_term, partner_bank_id, company_id)
        cadena = "Total a Cobrar: $ " +  str('{:,}'.format(partner.credit if partner.credit else 00)) +'   ' + '\nLimite de Credito: $ ' + str('{:,}'.format(partner.credit_limit if partner.credit_limit else 00 )) + '   '+ '\nCredito Excedido: $ ' + str('{:,}'.format(credit_exc if credit_exc else 00)) + '   ' + '\nFecha del Ultimo Pago: ' + date + '\n Le Recomendamos Realizar la Venta de Contado'
        warning['message'] = message + str(cadena)

        date_act = datetime.now().strftime('%Y-%m-%d')
        invoice_obj = self.pool.get('account.invoice')
        invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner.id),('type','=','out_invoice')])
        if invoice_overdue_ids:
            overdue_st = str(invoice_overdue_ids)
            warning_overdue = {
                        'title': "Error!",
                        'message': "El Cliente %s tiene las Facturas Vencias con los IDS:\n %s \n Solicitar pago o Vender de Contado!!!" % (partner.name,overdue_st,),
                }
            value_d = result.get('value',{})
            value_d['tipo_venta']= 'cash'

            return {'value': value_d, 'warning':warning_overdue}

        if partner.credit_limit < partner.credit:
            value_d = result.get('value',{})
            value_d['exced_credit']= True
            value_d['tipo_venta']= 'cash'

            return {'value': value_d, 'warning':warning}
        else:
            if partner.property_payment_term:
                value_d = result.get('value',{})
                value_d['tipo_venta']= 'credit'
                return {'value': value_d}
        return {'value': result.get('value',{})}



    def invoice_validate(self, cr, uid, ids, context=None):
        result =  super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        contado = False
        invoice_obj = self.pool.get('account.invoice')
        for order in self.browse(cr, uid, ids, context=context):
            ### REVISANDO ALBARANES POR FACTURAR ###
            partner_id = order.partner_id.id
            partner_br = order.partner_id
            if order.partner_id.is_company == False:
                partner_id = order.partner_id.parent_id.id
                partner_br = order.partner_id.parent_id
            stock_to_invoice_amount = 0.0
            stock_obj = self.pool.get('stock.picking.out')
            # cr.execute("select sum(amount_total) from sale_order where state='progress' and order_policy='picking' and partner_id=%s" % partner_br.id)
            # stock_to_invoice_amount = cr.fetchall()
            # if stock_to_invoice_amount[0][0] != None:
            #     stock_to_invoice_amount = stock_to_invoice_amount[0][0]
            # else:
            #     stock_to_invoice_amount = 0.0
            #cr.execute("select sum(product_qty) from stock_move where picking_id=%s and product_id=%s", (picking_id,pr))

            ### VERIFICANDO LOS LIMITES DE CREDITO
            credit_exc = 0.0
            account_lines = 0
            if order.tipo_venta == 'credit':

                if order.type == 'out_invoice':
                    if order.payment_term:
                        days = 0
                        for line_p in order.payment_term.line_ids:
                            days = line_p.days
                            account_lines += 1
                        if account_lines <= 1 and days == 0:
                            contado = True
                    ## Validando y Buscando Facturas Vencidas de Acuerdo a la Fecha de Vencimiento, el Estado y el monto pendiente > 0.0
                    date_act = datetime.now().strftime('%Y-%m-%d')
                    invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice'),('id','!=',ids[0])])
                    invoice_ids = invoice_obj.search(cr, uid, [('date_invoice','<=',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice'),('id','!=',ids[0])])

                    if partner_br.credit_limit == 0.0:
                        if contado == False:
                            raise osv.except_osv(
                                _('Error de Informacion! \n El Cliente %s ' % partner_br.name),
                                _('No tiene Definido Limite de Credito se encuentra en 0.0\n Pague de Contado o Agregue un Credito') )
                    # print "################################################## FACTURAS VENCIDAS", invoice_overdue_ids

                    # invoice_obj.write(cr, uid, invoice_overdue_ids, {'overdue_invoice':True})

                    # raise osv.except_osv(
                    #                     _('Flujo Interrumpido \n Las Facturas con los IDS %s estan Vencidas para el Cliente %s') % (invoice_overdue_ids, partner_br.name),
                    #                     _(''))
                    if invoice_overdue_ids:
                        ### Aqui Trataremos de Alternar que puedan desmarcar esas Facturas para que Puedan Validar la Nueva y en caso de que no entonces arrojar el mensaje
                        # overdue_ignored_ids = invoice_obj.search(cr, uid, [('overdue_invoice','=',False),('id','in',tuple(invoice_overdue_ids))])
                        # # print ">>>>>>>>>>>> FACTURAS QUE NO ESTAN IGNORADAS", overdue_ignored_ids
                        if partner_br.overdue_invoice == False:
                            raise osv.except_osv(
                                            _('Error de Validacion! \n Las Facturas con los IDS %s estan Vencidas para el Cliente %s') % (invoice_overdue_ids, partner_br.name),
                                            _('Favor de solicitar pago o vender de contado') )
                                            #_('Si necesita Omitir esta restriccion active el campo [Ignorar Facturas Vencidas] en la pestaña Contabilidad del Cliente') )
                    #if invoice_ids:
                    credit_total_partner = stock_to_invoice_amount + partner_br.credit

                    if credit_total_partner == 0:
                        credit_exc = 0.0
                    elif credit_total_partner > 0.0:
                        credit_exc = partner_br.credit_limit - credit_total_partner
                        if credit_exc < 0.0:
                            credit_exc = credit_exc * (-1)
                    if partner_br.credit_limit < credit_total_partner:
                        if contado == False:
                            raise osv.except_osv(
                                    _('No se puede Confirmar !'),
                                    _('El Cliente %s ah Excedido el Limite de Credito por la cantidad de %s \n Favor de solicitar pago o vender de contado' % (partner_br.name,str(credit_exc))))

                        # future_credit = order.partner_id.credit + order.amount_total
                        # if order.partner_id.credit_limit < future_credit:
                        #     order.write({'exced_credit':True})
                        # if order.partner_id.credit_limit < future_credit:
                            # if contado == False:
                            #     raise osv.except_osv(
                            #         _('No se puede Confirmar !\n El Cliente %s ah Excedido el Limite de Credito con esta Venta'  % order.partner_id.name),
                            #         _('Para autorizar Aumente el Limite de Credito'))
            return  result

    def create(self, cr, uid, vals, context=None):
        if 'tipo_venta' in vals:
            tipo_venta = vals['tipo_venta']
            if tipo_venta == 'cash':
                payment_obj = self.pool.get('account.payment.term')
                payment_ids = payment_obj.search(cr, uid,
                    [('line_ids','=',False)])
                if payment_ids:
                    vals.update({'payment_term':payment_ids[0]})
        return super(account_invoice, self).create(cr, uid, vals, context=context)


class sale_order_extend_credit(osv.osv_memory):
    _name = 'sale.order.extend.credit'
    _description = 'Asistente para Entender el Credito'
    _columns = {
    'partner_id': fields.many2one('res.partner', 'Cliente', readonly=True),
    'credit': fields.float('Total a Cobrar', digits=(12,2), readonly=True),
    'credit_limit': fields.float('Credito Concedito', digits=(12,2), readonly=True),
    'credit_extend': fields.float('Credito Nuevo', digits=(12,2), required=True, help='Indica el Nuevo Monto Autorizado de Credito, por defecto como sugerencia el Sistema Suma el Credito que Adeuda el Cliente + el monto del pedido de Venta' ),
    'password' : fields.char('Contraseña del Usuario', size=128, required=True),
    }

    def _get_partner(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        return sale_br.partner_id.id

    def _get_credit(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        return sale_br.partner_id.credit

    def _get_limit(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        return sale_br.partner_id.credit_limit

    def _get_credit_new(self, cr, uid, context=None):
        active_id = context.get('active_id', False)
        sale_obj = self.pool.get('account.invoice')
        sale_br = sale_obj.browse(cr, uid, [active_id], context=None)[0]
        credit_extend = sale_br.partner_id.credit + sale_br.amount_total
        return credit_extend

    _defaults = {

    'partner_id': _get_partner,
    'credit': _get_credit,
    'credit_limit': _get_limit,
    'credit_extend': _get_credit_new,

        }

    def auth(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', False)
        password = self.browse(cr, SUPERUSER_ID, ids, context=None)[0].password
        group_obj = self.pool.get('res.groups')
        group_id = group_obj.search(cr, SUPERUSER_ID, [('name','=','Ventas / Permisos Especiales')])
        users_obj = self.pool.get('res.users')
        user_list = []
        sale_order_obj = self.pool.get('account.invoice')
        for group in group_obj.browse(cr, SUPERUSER_ID, group_id, context=None):
            for user in group.users:
                user_list.append(user.id)
        if user_list:
            user_ids = users_obj.search(cr, SUPERUSER_ID, [('password','=',password),('id','in',tuple(user_list))])
            if user_ids:
                if active_ids:
                    partner_obj = self.pool.get('res.partner')
                    for rec in self.browse(cr, uid, ids, context=None):
                        sale_order_obj.write(cr, uid, active_ids, {'exced_credit': False})
                        partner_obj.write(cr, uid, [rec.partner_id.id], {'credit_limit': rec.credit_extend})
                return {'type' : 'ir.actions.act_window_close' }
            else:
                raise osv.except_osv(
                                    _('Error ! \n La Contraseña es Incorrecta o el Usuario no tiene Permisos.'),
                                    _('Consulte a su Administrador y Verifique que el usuario se encuentra en el Grupo [Ventas / Permisos Especiales]'))

        else:
            raise osv.except_osv(
                    _('Error ! \n La Contraseña es Incorrecta o el Usuario no tiene Permisos.'),
                    _('Consulte a su Administrador y Verifique que el usuario se encuentra en el Grupo [Ventas / Permisos Especiales]'))
        return {'type' : 'ir.actions.act_window_close' }

sale_order_extend_credit()


######### HERENCIA DE FACTURACION DESDE ALBARANES ##############
# class stock_partial_picking(osv.osv):
#     _name = 'stock.partial.picking'
#     _inherit ='stock.partial.picking'
#     _columns = {
#         }

#     def do_partial(self, cr, uid, ids, context=None):
#         res = super(stock_partial_picking, self).do_partial(cr, uid, ids, context)

#         return res

# stock_partial_picking()
