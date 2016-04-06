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
####### CREAMOS POR HERENCIA UN MODELO DE PEDIDOS DE VENTA PARA MOSTRADOR ####
####### HEREDA DEL MODELO BASE SALE.ORDER ########
class sale_order_counter(osv.osv):
    _name = "sale.order.counter"
    _inherit = "sale.order"
    _table = "sale_order"
    _description = "Counter Orders"
    _columns = {
        'product_on_id':fields.char('Producto', required=False, help="""Ingresa el Codigo del Producto Automaticamente se Agregara como linea tomando El precio del producto y su unidad de Medida
        Podemos Agregar los Siguientes Comodines:
            - Si queremos agregar el Producto y la Cantidad a la Vez ponemos el Codigo del Producto + Cantidad, es importante poner el simbolo + despues del Producto'""" ),
        'pricelist_currency':fields.selection([
        ('mxn','MXN'),
        ('usd','USD'),
         ],    'Tarifa de Venta', select=True),
        'venta_mostrador': fields.boolean('Venta de Mostrador'),
        'sale_id': fields.many2one('sale.order','Pedido de Venta', help='Pedido de Venta Creado a partir de una Venta de Mostrador', readonly=True ),
        'tipo_venta': fields.selection([('credit','Credito'),('cash','Contado')], 'Plazo'),
        }

    _defaults = {  
        'state': 'draft',
        'pricelist_currency': 'mxn',
        'venta_mostrador': True,
        'tipo_venta': 'cash',
        }

    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj

    def onchange_partner_counter_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        if part.is_company == False:
            part = part.parent_id
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
        }
        if pricelist:
            val['pricelist_id'] = pricelist

        warning = {}
        title = False
        message = False
        partner = part
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

        date_act = datetime.now().strftime('%Y-%m-%d')
        invoice_obj = self.pool.get('account.invoice')
        invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner.id),('type','=','out_invoice')])
        if invoice_overdue_ids:
            overdue_st = str(invoice_overdue_ids)
            warning_overdue = {
                        'title': "Error!",
                        'message': "El Cliente %s tiene las Facturas Vencias con los IDS:\n %s \n Solicitar pago o Vender de Contado!!!" % (partner.name,overdue_st,),
                }
            value_d = val
            value_d['tipo_venta']= 'cash'

            return {'value': value_d, 'warning':warning_overdue}
        account_voucher_obj = self.pool.get('account.voucher')
        account_voucher_ids = account_voucher_obj.search(cr, uid, [('partner_id','=',partner.id)])
        date = ''
        for voucher in account_voucher_obj.browse(cr, uid, account_voucher_ids, context=None):
            if voucher.date > date:
                date = voucher.date
        if not account_voucher_ids:
            date = 'No se ah detectado Pago'

        cadena = "Total a Cobrar: $ " +  str('{:,}'.format(partner.credit if partner.credit else 00)) +'   ' + '\nLimite de Credito: $ ' + str('{:,}'.format(partner.credit_limit if partner.credit_limit else 00)) + '   '+ '\nCredito Excedido: $ ' + str('{:,}'.format(credit_exc if credit_exc else 00)) + '   ' + '\nFecha del Ultimo Pago: ' + date + '\n Le Recomendamos Realizar la Venta de Contado'
        warning['message'] = message + str(cadena)
        if partner.credit_limit < partner.credit:
            value_d = val
            value_d['tipo_venta']= 'cash'

            return {'value': value_d, 'warning':warning}
        else:
            value_d = val
            if partner.property_payment_term:
                
                value_d['tipo_venta']= 'credit'
            return {'value': value_d}

        return {'value': val}

    ### No permitir Duplicar Registros ###
    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(
            _('Error!'),
            _('Para evitar Erorres se ah Restringido la Duplicacion de Registros.\n Por favor Cree uno Nuevo') )
        return super(sale_order_counter, self).copy(cr, uid, id, default, context=context)

    #### ON CHANGE CREDITO ####
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

    def action_cancel_sale(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'cancel'}, context=None)
        return True

    def reactive_sale(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'}, context=None)
        return True

    def copy_quotation_sale(self, cr, uid, ids, context=None):
        id = self.copy(cr, uid, ids[0], context=None)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'counter_sales', 'view_order_form_counter')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Venta Mostrador'),
            'res_model': 'sale.order.counter',
            'res_id': id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def action_button_confirm_sale(self, cr, uid, ids, context=None):
        lines = []
        sale_obj = self.pool.get('sale.order')
        ###### VALIDANDO EL CREDITO DEL CLIENTE #####

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
            # cr.execute("select sum(amount_total) from sale_order where state='progress' and order_policy='picking' and partner_id=%s and id !=%s" % (partner_id,ids[0]))

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
                ## Validando y Buscando Facturas Vencidas de Acuerdo a la Fecha de Vencimiento, el Estado y el monto pendiente > 0.0
                date_act = datetime.now().strftime('%Y-%m-%d')
                invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice')])
                invoice_ids = invoice_obj.search(cr, uid, [('date_invoice','<=',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice')])
                
                if partner_br.credit_limit == 0.0:
                    raise osv.except_osv(
                        _('Error de Informacion! \n El Cliente %s ' % partner_br.name),
                        _('No tiene Definido Limite de Credito se encuentra en 0.0\n Pague de Contado o Agregue un Credito') )
                # print "################################################## FACTURAS VENCIDAS", invoice_overdue_ids

                # invoice_obj.write(cr, uid, invoice_overdue_ids, {'overdue_invoice':True})

                # raise osv.except_osv(
                #                     _('Flujo Interrumpido \n Las Facturas con los IDS %s estan Vencidas para el Cliente %s') % (invoice_overdue_ids, order.partner_id.name),
                #                     _(''))
                if invoice_overdue_ids:
                    ### Aqui Trataremos de Alternar que puedan desmarcar esas Facturas para que Puedan Validar la Nueva y en caso de que no entonces arrojar el mensaje
                    # overdue_ignored_ids = invoice_obj.search(cr, uid, [('overdue_invoice','=',False),('id','in',tuple(invoice_overdue_ids))])
                    # print ">>>>>>>>>>>> FACTURAS QUE NO ESTAN IGNORADAS", overdue_ignored_ids
                    if partner_br.overdue_invoice == False:
                        raise osv.except_osv(
                                        _('Error de Validacion! \n Las Facturas con los IDS %s estan Vencidas para el Cliente %s') % (invoice_overdue_ids, partner_br.name),
                                        _('Favor de solicitar pago o vender de contado') )

                #if invoice_ids:
                if order.company_id.currency_id.id != order.currency_id.id:
                    cr.execute("select rate from res_currency_rate where currency_id=%s and name<= %s order by name desc limit 1", (order.currency_id.id, order.date_order,))
                    #pediment_qty = cr.fetchall()[0][0]
                    currency_tc = cr.fetchall()[0][0]
                    order_amount_total = order.amount_total/currency_tc
                    credit_total_partner = stock_to_invoice_amount + partner_br.credit + order_amount_total

                else:
                    credit_total_partner = stock_to_invoice_amount + partner_br.credit + order.amount_total

                if credit_total_partner == 0:
                    credit_exc = 0.0
                elif credit_total_partner > 0.0:
                    credit_exc = partner_br.credit_limit - credit_total_partner
                    if credit_exc < 0.0:
                        credit_exc = credit_exc * (-1)
                if partner_br.credit_limit < credit_total_partner:
                    raise osv.except_osv(
                            _('No se puede Confirmar !'),
                            _('El Cliente %s ah Excedido el Limite de Credito por la cantidad de %s \n Favor de solicitar pago o vender de contado' % (partner_br.name,str(credit_exc))))
        
        ##### CONFIRMANDO EL PEDIDO DE VENTA Y CREANDOLO ####  

        for rec in self.browse(cr, uid, ids, context=None):
            for line in rec.order_line:
                xline = (0,0,{
                    'state': line.state,
                    'name': line.name if line.name else '',
                    'product_id': line.product_id.id if line.product_id else False,
                    'product_uom_qty': line.product_uom_qty if line.product_uom_qty else False,
                    'product_uom': line.product_uom.id if line.product_uom else False,
                    'product_uos_qty': line.product_uos_qty if line.product_uos_qty else False,
                    'product_uos': line.product_uos.id if line.product_uos else False,
                    'price_unit': line.product_id.list_price if line.product_id else False,
                    'discount': line.discount if line.discount else False,
                    'tax_id': [(6, 0,[line.id for line in line.tax_id])] if line.tax_id else False,
                    })
                lines.append(xline)

            vals ={
                'partner_id': rec.partner_id.id if rec.partner_id else False,
                'partner_invoice_id': rec.partner_invoice_id.id if rec.partner_invoice_id else False,
                'partner_shipping_id': rec.partner_shipping_id.id if rec.partner_shipping_id else False,
                'project_id': rec.project_id.id if rec.project_id else False,
                'invoice_exists': rec.invoice_exists if rec.invoice_exists else False,
                'user_id': rec.user_id.id if rec.user_id else False,
                'date_order': rec.date_order if rec.date_order else False,
                'shop_id': rec.shop_id.id if rec.shop_id else False,
                'client_order_ref': rec.client_order_ref if rec.client_order_ref else False,
                #'pricelist_currency': rec.pricelist_currency if rec.pricelist_currency else False,
                'pricelist_id': rec.pricelist_id.id if rec.pricelist_id else False,
                'origin': rec.origin if rec.origin else False,
                'payment_term': rec.payment_term.id if rec.payment_term else False,
                'fiscal_position': rec.fiscal_position.id if rec.fiscal_position else False,
                'company_id': rec.company_id.id if rec.company_id else False,
                'invoiced': rec.invoiced if rec.invoiced else False,
                'order_line': [x for x in lines],
                'payment_term': rec.payment_term.id if rec.payment_term else False,
                'tipo_venta': rec.tipo_venta,
                'order_policy': 'manual',
            }
            sale_id = sale_obj.create(cr, uid, vals, context=None)

            for sale_created in sale_obj.browse(cr, uid, [sale_id], context=None):
                sale_created.write({'origin':rec.name})
                sale_created.action_button_confirm()
            rec.write({'state':'progress','sale_id':sale_id})
        return {
                    'type': 'ir.actions.act_window',
                    'name': _('Pedido de Venta'),
                    'res_model': 'sale.order',
                    'res_id': sale_id,
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'target': 'current',
                    'nodestroy': True,
                }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            #vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order.counter') or '/'
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order.counter') or '/'
        return super(sale_order_counter, self).create(cr, uid, vals, context=context)

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    def on_change_pricelist_currency(self, cr, uid, ids, partner_id, pricelist_currency, context=None):
        res= {}
        if partner_id:
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.browse(cr, SUPERUSER_ID, partner_id, context=None)
            pricelist = self.pool.get('product.pricelist').search(cr, SUPERUSER_ID,[('type','=','sale')])
            try:
                if pricelist_currency == 'mxn':
                    res['pricelist_id'] = partner.property_product_pricelist.id
                else:
                    if not partner.property_product_pricelist_usd:
                        res['pricelist_id'] = partner.property_product_pricelist.id
                        warning = {
                            'title':'Error !',
                            'message':'No se Tiene Lista de Precios en USD para el Cliente %s' %(partner.name,)}
                        return {'value':res,'warning':warning}
                    else:
                        res['pricelist_id'] = partner.property_product_pricelist_usd.id
            except:
                res['pricelist_id'] = pricelist[0]
                warning = {
                            'title':'Error !',
                            'message':'No se Tiene Lista de Precios en USD o en MXN para el Cliente %s' %(partner.name,)}
                return {'value':res,'warning':warning}
        return {'value':res}

    def on_change_load_products(self, cr, uid, ids, company_id, partner_id, product_on_id, order_line, pricelist_id, context=None):
        # pos_line_obj = self.pool.get('pos.order.line')
        product_obj = self.pool.get('product.product')
        salesman_obj = self.pool.get('res.users')
        partner_obj = self.pool.get('res.partner')
        if partner_id:
            partner = partner_obj.browse(cr, uid, partner_id, context=None)
            lines = order_line

            fpos_obj = self.pool.get('account.fiscal.position')
            fpos = partner.property_account_position.id or False
            fpos = fpos and fpos_obj.browse(cr, uid, fpos, context=context) or False
            # tax_id = [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product[0].taxes_id)])],

            if not product_on_id:
                return {}
            if '+' in product_on_id:
                try:
                    cod_product = product_on_id.split('+')[1]
                    qty_product = product_on_id.split('+')[0]
                    # print " CODIGO DEL VENDEDOR",sale_tpv_cod
                    product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
                    product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
                    if product_br.default_code:
                        product_name = ' [ '+product_br.default_code +' ] '+product_br.name
                    else:
                        product_name = product_br.name
                    if product_id:
                        product_pricelist = 0.0
                        if not pricelist_id:
                            product_pricelist = product_br.list_price
                        else:
                            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                            product_pricelist = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
                                    product_id[0], int(qty_product) or 1.0, partner_id, {
                                        'uom': product_br.uom_id.id,
                                        'date': date_order,
                                        })[pricelist_id]

                        xline = (0,0,{
                                'product_id': product_id[0],
                                'name': product_name,
                                'tax_id': [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_br.taxes_id)])],
                                'product_uom_qty': int(qty_product),
                                'price_unit': product_pricelist,
                                'product_uom': product_br.uom_id.id,
                            })
                        lines.append(xline)
                    else:
                        warning = {
                                    'title': 'Error Captura!',
                                    'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
                                }
                        return {'value' : {'product_on_id':False,},'warning':warning}
                except:
                    warning = {
                            'title':'Error !',
                            'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
                             \n -[Cantidad+CodigoProducto]'}
                    return {'value' : {'product_on_id':False,},'warning':warning}
            else:
                try:
                    cod_product = product_on_id
                    qty_product = 1
                    # print " CODIGO DEL VENDEDOR",sale_tpv_cod
                    product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
                    product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
                    if product_br.default_code:
                        product_name = ' [ '+product_br.default_code +' ] '+product_br.name
                    
                    else:
                        product_name = product_br.name
                    if product_id:
                        product_pricelist = 0.0
                        if not pricelist_id:
                            product_pricelist = product_br.list_price
                        else:
                            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
                            product_pricelist = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_id],
                                    product_id[0], int(qty_product) or 1.0, partner_id, {
                                        'uom': product_br.uom_id.id,
                                        'date': date_order,
                                        })[pricelist_id]
                        xline = (0,0,{
                                'product_id': product_id[0],
                                'name': product_name,
                                'tax_id': [(6, 0, [_w for _w in fpos_obj.map_tax(cr, uid, fpos, product_br.taxes_id)])],
                                'product_uom_qty': int(qty_product),
                                'price_unit': product_pricelist,
                                'product_uom': product_br.uom_id.id,
                            })
                        lines.append(xline)
                    else:
                        warning = {
                                    'title': 'Error Captura!',
                                    'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
                                }
                        return {'value' : {'product_on_id':False,},'warning':warning}
                except:
                    warning = {
                            'title':'Error !',
                            'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
                             \n -[Cantidad+CodigoProducto]'}
                    return {'value' : {'product_on_id':False,},'warning':warning}

        else:
            lines = order_line

            tax_id = []

            if not product_on_id:
                return {}
            if '+' in product_on_id:
                try:
                    cod_product = product_on_id.split('+')[1]
                    qty_product = product_on_id.split('+')[0]
                    # print " CODIGO DEL VENDEDOR",sale_tpv_cod
                    product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
                    product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
                    for tx in product_br.taxes_id:
                        if tx.company_id.id == company_id:
                            tax_id.append(tx.id)
                    if product_br.default_code:
                        product_name = '['+product_br.default_code +']'+product_br.name
                    else:
                        product_name = product_br.name

                    if product_id:
                        xline = (0,0,{
                                'product_id': product_id[0],
                                'name': product_name,
                                'tax_id': [(6, 0, tax_id)],
                                'product_uom_qty': int(qty_product),
                                'price_unit': product_br.list_price,
                                'product_uom': product_br.uom_id.id,
                            })
                        lines.append(xline)
                    else:
                        warning = {
                                    'title': 'Error Captura!',
                                    'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
                                }
                        return {'value' : {'product_on_id':False,},'warning':warning}
                except:
                    warning = {
                            'title':'Error !',
                            'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
                             \n -[Cantidad+CodigoProducto]'}
                    return {'value' : {'product_on_id':False,},'warning':warning}
            else:
                try:
                    cod_product = product_on_id
                    qty_product = 1
                    # print " CODIGO DEL VENDEDOR",sale_tpv_cod
                    product_id = product_obj.search(cr, uid, ['|',('default_code','=',cod_product),('ean13','=',cod_product)])
                    product_br = product_obj.browse(cr, uid, product_id, context=None)[0]
                    if product_br.default_code:
                        product_name = '['+product_br.default_code +']'+product_br.name
                    else:
                        product_name = product_br.name

                    for tx in product_br.taxes_id:
                        if tx.company_id.id == company_id:
                            tax_id.append(tx.id)
                    if product_id:
                        xline = (0,0,{
                                'product_id': product_id[0],
                                'name': product_name,
                                'tax_id': [(6, 0, tax_id)],
                                'product_uom_qty': int(qty_product),
                                'price_unit': product_br.list_price,
                                'product_uom': product_br.uom_id.id,
                            })
                        lines.append(xline)
                    else:
                        warning = {
                                    'title': 'Error Captura!',
                                    'message': 'El Codigo Capturado no Encontro Ningun Producto en la Base de Datos, Codigo %s' % (cod_product,),
                                }
                        return {'value' : {'product_on_id':False,},'warning':warning}
                except:
                    warning = {
                            'title':'Error !',
                            'message':'La Informacion Introducida Contiene Errores Verificar que el orden de la informacion sea de los ejemplos:\
                             \n -[Cantidad+CodigoProducto]'}
                    return {'value' : {'product_on_id':False,},'warning':warning}

          
        return {'value' : {'product_on_id':False,'order_line':[x for x in lines]}}

sale_order_counter()

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit ='res.partner'
    def _credit_debit_get(self, cr, uid, ids, field_names, arg, context=None):
        ctx = context.copy()
        ctx['all_fiscalyear'] = True
        query = self.pool.get('account.move.line')._query_get(cr, uid, context=ctx)
        cr.execute("""SELECT l.partner_id, a.type, SUM(l.debit-l.credit)
                      FROM account_move_line l
                      LEFT JOIN account_account a ON (l.account_id=a.id)
                      WHERE a.type IN ('receivable','payable')
                      AND l.partner_id IN %s
                      AND l.reconcile_id IS NULL
                      AND """ + query + """
                      GROUP BY l.partner_id, a.type
                      """,
                   (tuple(ids),))
        maps = {'receivable':'credit', 'payable':'debit' }
        res = {}
        for id in ids:
            res[id] = {}.fromkeys(field_names, 0)
        for pid,type,val in cr.fetchall():
            if val is None: val=0
            res[pid][maps[type]] = (type=='receivable') and val or -val
        return res


    def _credit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(cr, uid, obj, name, 'receivable', args, context=context)

    def _debit_search(self, cr, uid, obj, name, args, context=None):
        return self._asset_difference_search(cr, uid, obj, name, 'payable', args, context=context)

    _columns = {
        'stock_to_invoice_amount': fields.float('Monto de Albaranes Por Facturar', digits=(14,4)),
        'credit': fields.function(_credit_debit_get,
            fnct_search=_credit_search, string='Total Receivable', multi='dc', help="Total amount this customer owes you."),
        'debit': fields.function(_credit_debit_get, fnct_search=_debit_search, string='Total Payable', multi='dc', help="Total amount you have to pay to this supplier."),
        }

    _defaults = {
        }
res_partner()


class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit ='sale.order'
    _columns = {
        'tipo_venta': fields.selection([('credit','Credito'),('cash','Contado')], 'Plazo'),
        }


    _defaults = {  
        'tipo_venta': 'cash',
        'order_policy': 'picking',
        }

    def get_current_instance(self, cr, uid, id):
        lines = self.browse(cr,uid,id)
        obj = None
        for i in lines:
            obj = i
        return obj

    def onchange_partner_id(self, cr, uid, ids, part, context=None):

        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=None)
        if part:
            warning = {}
            title = False
            message = False
            partner = self.pool.get('res.partner').browse(cr, uid, part, context=None)
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

            account_voucher_obj = self.pool.get('account.voucher')
            account_voucher_ids = account_voucher_obj.search(cr, uid, [('partner_id','=',partner.id)])
            date = ''
            for voucher in account_voucher_obj.browse(cr, uid, account_voucher_ids, context=None):
                if voucher.date > date:
                    date = voucher.date
            if not account_voucher_ids:
                date = 'No se ah detectado Pago'

            cadena = "Total a Cobrar: $ " +  str('{:,}'.format(partner.credit if partner.credit else 00)) +'   ' + '\nLimite de Credito: $ ' + str('{:,}'.format(partner.credit_limit if partner.credit_limit else 00)) + '   '+ '\nCredito Excedido: $ ' + str('{:,}'.format(credit_exc if credit_exc else 00)) + '   ' + '\nFecha del Ultimo Pago: ' + date + '\n Le Recomendamos Realizar la Venta de Contado'
            warning['message'] = message + str(cadena)
            if partner.credit_limit < partner.credit:
                value_d = result.get('value',{})
                value_d['tipo_venta']= 'cash'

                return {'value': value_d, 'warning':warning}
            else:
                value_d = result.get('value',{})
                if partner.property_payment_term:
                    value_d['tipo_venta']= 'credit'
                return {'value': value_d}

        return result

    def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
        res  = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_invoice, context)
        account_obj = self.pool.get('account.invoice')
        self_br = self.browse(cr, uid, ids[0], context=None)
        tipo_venta = self_br.tipo_venta
        account_obj.write(cr, uid, [res], {'tipo_venta':tipo_venta}, context=None)
        return res
    #### ON CHANGE CREDITO ####

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

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'venta_mostrador': False,
            'tipo_venta': False,
        })
        return super(sale_order, self).copy(cr, uid, id, default, context=context)

    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context)
        lines = []
        sale_obj = self.pool.get('sale.order')
        ###### VALIDANDO EL CREDITO DEL CLIENTE #####

        invoice_obj = self.pool.get('account.invoice')
        contado = False
        invoice_obj = self.pool.get('account.invoice')

        for order in self.browse(cr, uid, ids, context=context):
    
            partner_id = order.partner_id.id
            partner_br = order.partner_id
            if order.partner_id.is_company == False:
                partner_id = order.partner_id.parent_id.id
                partner_br = order.partner_id.parent_id
            ### REVISANDO ALBARANES POR FACTURAR ###
            stock_to_invoice_amount = 0.0
            stock_obj = self.pool.get('stock.picking.out')
            # cr.execute("select sum(amount_total) from sale_order where state='progress' and order_policy='picking' and partner_id=%s and id !=%s" % (partner_br.id,ids[0]))
            # stock_to_invoice_amount = cr.fetchall()
            # if stock_to_invoice_amount[0][0] != None:
            #     stock_to_invoice_amount = stock_to_invoice_amount[0][0]
            # else:
            #     stock_to_invoice_amount = 0.0
            #cr.execute("select sum(product_qty) from stock_move where picking_id=%s and product_id=%s", (picking_id,pr))
            ### VERIFICANDO LOS LIMITES DE CREDITO
            credit_exc = 0.0
            account_lines = 0
            if order.tipo_venta == 'credit' or not order.tipo_venta:
                if order.payment_term:
                    days = 0
                    for line_p in order.payment_term.line_ids:
                        days = line_p.days
                        account_lines += 1
                    if account_lines <= 1 and days == 0:
                        contado = True
                ## Validando y Buscando Facturas Vencidas de Acuerdo a la Fecha de Vencimiento, el Estado y el monto pendiente > 0.0
                date_act = datetime.now().strftime('%Y-%m-%d')
                invoice_overdue_ids = invoice_obj.search(cr, uid, [('date_due','<',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice')])
                invoice_ids = invoice_obj.search(cr, uid, [('date_invoice','<=',date_act),('state','=','open'),('residual','>',0.0),('partner_id','=',partner_br.id),('type','=','out_invoice')])
                
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
                if contado == True:
                    return res
                if invoice_overdue_ids :
                    ### Aqui Trataremos de Alternar que puedan desmarcar esas Facturas para que Puedan Validar la Nueva y en caso de que no entonces arrojar el mensaje
                    # overdue_ignored_ids = invoice_obj.search(cr, uid, [('overdue_invoice','=',False),('id','in',tuple(invoice_overdue_ids))])
                    # print ">>>>>>>>>>>> FACTURAS QUE NO ESTAN IGNORADAS", overdue_ignored_ids
                    if partner_br.overdue_invoice == False:
                        raise osv.except_osv(
                                        _('Error de Validacion! \n Las Facturas con los IDS %s estan Vencidas para el Cliente %s') % (invoice_overdue_ids, partner_br.name),
                                        _('Favor de solicitar pago o vender de contado') )
                #if invoice_ids:
                #if invoice_ids:
                if order.company_id.currency_id.id != order.currency_id.id:
                    cr.execute("select rate from res_currency_rate where currency_id=%s and name<= %s order by name desc limit 1", (order.currency_id.id, order.date_order,))
                    #pediment_qty = cr.fetchall()[0][0]
                    currency_tc = cr.fetchall()[0][0]
                    order_amount_total = order.amount_total/currency_tc
                    credit_total_partner = stock_to_invoice_amount + partner_br.credit + order_amount_total

                else:
                    credit_total_partner = stock_to_invoice_amount + partner_br.credit + order.amount_total

                if credit_total_partner == 0:
                    credit_exc = 0.0
                elif credit_total_partner > 0.0:
                    credit_exc = partner_br.credit_limit - credit_total_partner
                    if credit_exc < 0.0:
                        credit_exc = credit_exc * (-1)
                if partner_br.credit_limit < credit_total_partner:
                    raise osv.except_osv(
                            _('No se puede Confirmar !'),
                            _('El Cliente %s ah Excedido el Limite de Credito por la cantidad de %s \n Favor de solicitar pago o vender de contado' % (partner_br.name,str(credit_exc))))
        # ############## INTERRUPCION DEL FLUJO PYTHON ############################
        # raise osv.except_osv(_('Interrupcion del Flujo!'), 
        #                      _('Debugeando el Codigo de Creacion de Factura desde lineas de Compra') )

        return res
    # #### AQUI VAMOS A CONFIRMAR EL PICKING DE SALIDA SIEMPRE Y CUANDO HAYA EXISTENCIAS ####
    # def action_ship_create(self, cr, uid, ids, context=None):
    #     res = super(sale_order, self).action_ship_create(cr, uid, ids, context=None)
    #     stock_obj = self.pool.get('stock.picking')
    #     for order in self.browse(cr, uid, ids, context=context):
    #         supervisor_id = uid
    #         #     raise osv.except_osv(
    #         #         _('Error !'),
    #         #         _('El supervisor de la tienda %s no puede confirmar el pedido mediante el Boton de Confirmar pedido, utilice el Asistende de concliacion de Mercancia y Ejecute el Boton Conciliar Mercancia'  % (order.shop_id.name,)))
    #         # else:
    #         for stock in order.picking_ids:
    #             stock_id = stock.id
    #             stock_partial_picking_obj = self.pool.get('stock.partial.picking')
    #             stock_partial_picking_lines_obj = self.pool.get('stock.partial.picking.line')
    #             ########## LAS SIGUIENTES LINEAS SIMULAN EL WIZARD QUE CONFIRMA EL ALBARAN DE SALIDA, LA CONDICION PARA CONDIRMAR EL ALBARAN ES NECESARIO QUE  LA ORDEN CONTENGA UN KIT DE REFERENCIA
    #             if order.kit_reference_id or order.confirmed_albaran == True:
    #                 stock.draft_validate()
    #                 stock_lines = []
    #                 # today = time.strftime( DEFAULT_SERVER_DATETIME_FORMAT)
    #                 for move in stock.move_lines:
    #                     move.action_confirm()
    #                     # move.force_assign()
    #                     xline = (0 ,0,{
    #                                     'product_id' : move.product_id.id,
    #                                     'quantity' : move.product_qty,
    #                                     'product_uom': move.product_uom.id,
    #                                     #'prodlot_id' : False,
    #                                     'location_id': move.location_id.id or False,
    #                                     'location_dest_id': move.location_dest_id.id or False,
    #                                     'move_id' : move.id,
    #                                     #'wizard_id' : ,
    #                                     #'update_cost': fields.boolean('Need cost update'),
    #                                     #'cost' : fields.float("Cost", help="Unit Cost for this product line"),
    #                                     #'currency' : fields.many2one('res.currency', string="Currency", help="Currency in which Unit cost is expressed", ondelete='CASCADE'),
    #                                     #'tracking': fields.function(_tracking, string='Tracking', type='boolean'), 
    #                                     })
    #                     stock_lines.append(xline)
    #                 vals ={
    #                         'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #                         'picking_id': stock.id,
    #                         'hide_tracking': False,
    #                         'move_ids' : [x for x in stock_lines],
    #                         }
    #                 stock_partial_picking_id = stock_partial_picking_obj.create(cr, uid, vals, context)
    #                 for partial_picking in stock_partial_picking_obj.browse(cr, uid, [stock_partial_picking_id], context=context):
    #                     for partial_picking_lines in partial_picking.move_ids:
    #                         partial_picking.do_partial()
    #                     # move.action_done()
    #                     # move.action_assign()
    #                 # stock.action_process()
    #                     # wf_service = netsvc.LocalService("workflow")  ### CON ESTAS LINEAS DISPARAMOS EL WORKFLOW PARA NO REALIZARLO MEDIANTE FUNCIONES
    #                     # wf_service.trg_validate(uid, 'stock.picking', stock.id, 'test_done', cr) ####### SIMULA EL BOTON CONFIRMAR STOCK PICKING ALBARAN SALIDA
    #                 # self.action_process_picking(cr, uid, ids, stock_id, context=None)
    #     return res

sale_order()

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _inherit ='sale.order.line'
    _columns = {
        }

    _defaults = {
        }

sale_order_line()

################################################
class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit ='res.partner'
    _columns = {
        'property_product_pricelist_usd': fields.many2one('product.pricelist', "Sale Pricelist",
            domain=[('type','=','sale')],
            help="Tarifa de Venta en USD"),
        }

    _defaults = {
        }
res_partner()


class stock_invoice_onshipping(osv.osv_memory):
    _name = 'stock.invoice.onshipping'
    _inherit ='stock.invoice.onshipping'
    _columns = {
        }

    _defaults = {
        }
        
    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        picking_pool = self.pool.get('stock.picking')
        onshipdata_obj = self.read(cr, uid, ids, ['journal_id', 'group', 'invoice_date'])
        if context.get('new_picking', False):
            onshipdata_obj['id'] = onshipdata_obj.new_picking
            onshipdata_obj[ids] = onshipdata_obj.new_picking
        context['date_inv'] = onshipdata_obj[0]['invoice_date']
        active_ids = context.get('active_ids', [])
        picking_not_send_ids = picking_pool.search(cr, uid, [('state','!=','done'),('id','in',tuple(active_ids))])
        if picking_not_send_ids:
            cr.execute("select name from stock_picking where id in %s",(tuple(picking_not_send_ids),))
            picking_not_send = [ str(x[0]) for x in cr.fetchall()]
            raise osv.except_osv(
                _('Error !'),
                _('Los Albaranes ** %s ** que intenta Facturar, no se encuentran en estado Entregado, asi que no se pueden Facturar.\n Consulte al Administrador '  % (str(picking_not_send),)))
        active_picking = picking_pool.browse(cr, uid, context.get('active_id',False), context=context)
        inv_type = picking_pool._get_invoice_type(active_picking)
        sale_obj = self.pool.get('sale.order')
        sale_id = sale_obj.search(cr, uid, [('name','=',active_picking.origin)], context=None)
        if sale_id:
            sale_br = sale_obj.browse(cr, uid, sale_id, context=None)[0]
        context['inv_type'] = inv_type
        if isinstance(onshipdata_obj[0]['journal_id'], tuple):
            onshipdata_obj[0]['journal_id'] = onshipdata_obj[0]['journal_id'][0]
        res = picking_pool.action_invoice_create(cr, uid, active_ids,
              journal_id = onshipdata_obj[0]['journal_id'],
              group = onshipdata_obj[0]['group'],
              type = inv_type,
              context=context)
        if type(res) == type({}):
            tipo_venta = 'credit'
            for d in res:
                invoice_obj = self.pool.get('account.invoice')
                invoice_id = res[d]
                for invoice in invoice_obj.browse(cr, uid, [invoice_id], context=None):
                    partner_br = invoice.partner_id
                    vals_w = {}
                    if not sale_id:
                        if invoice.partner_id.parent_id:
                            partner_br = invoice.partner_id.parent_id
                        if partner_br.property_payment_term:
                            if partner_br.credit < partner_br.credit_limit:
                                vals_w = {'tipo_venta':'credit',
                                'payment_term':invoice.partner_id.property_payment_term.id}
                                tipo_venta = 'credit'
                            else:
                                payment_obj = self.pool.get('account.payment.term')
                                payment_ids = payment_obj.search(cr, uid,
                                        [('line_ids','=',False)])
                                vals_w = {'tipo_venta':'cash', 'payment_term':payment_ids[0] if payment_ids else False }
                        else:
                            payment_obj = self.pool.get('account.payment.term')
                            payment_ids = payment_obj.search(cr, uid,
                                        [('line_ids','=',False)])
                            vals_w = {'tipo_venta':'cash', 'payment_term':payment_ids[0] if payment_ids else False }
                    else:
                        if sale_br.tipo_venta == 'cash':
                            payment_obj = self.pool.get('account.payment.term')
                            payment_ids = payment_obj.search(cr, uid,
                                        [('line_ids','=',False)])
                            vals_w = {
                            'payment_term': payment_ids[0] if payment_ids else False,
                            'tipo_venta': sale_br.tipo_venta,
                                }
                        else:
                            vals_w = {
                                'payment_term': sale_br.partner_id.property_payment_term.id if sale_br.partner_id.property_payment_term else False,
                                'tipo_venta': sale_br.tipo_venta,
                                    }
                    invoice.write(vals_w)
        return res

stock_invoice_onshipping()