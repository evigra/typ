# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools
from openerp import netsvc
from openerp import release
import datetime
from pytz import timezone
import pytz
from dateutil.relativedelta import relativedelta

import time
import os

class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit ='account.invoice.line'
    _columns = {
    'company_recl_id': fields.integer('Compañia Referencia Recl.', help='Referencia de Compañia para Reclasificacion', )
        }

    _defaults = {
        }

class purchase_line_invoice(osv.osv_memory):
    _name = 'purchase.order.line_invoice'
    _inherit ='purchase.order.line_invoice'
    _columns = {
        'reclasification': fields.boolean('Reclasificacion Automatica de Fletes',
            help=""" Si Activa esta Opcion en Automatico el Sistema Generara los Asientos Contables para cada Compañia a quien pertenecen las Lineas.
            Agrupadas por El Monto de Cada una de Ellas.""", ),
        }

    _defaults = {
        }

    def makeInvoices(self, cr, uid, ids, context=None):
        """
             To get Purchase Order line and create Invoice
             @param self: The object pointer.
             @param cr: A database cursor
             @param uid: ID of the user currently logged in
             @param context: A standard dictionary
             @return : retrun view of Invoice
        """

        if context is None:
            context={}

        record_ids =  context.get('active_ids',[])
        if record_ids:
            res = False
            invoices = {}
            invoice_obj = self.pool.get('account.invoice')
            purchase_obj = self.pool.get('purchase.order')
            purchase_line_obj = self.pool.get('purchase.order.line')
            invoice_line_obj = self.pool.get('account.invoice.line')
            account_jrnl_obj = self.pool.get('account.journal')

            def multiple_order_invoice_notes(orders):
                notes = ""
                for order in orders:
                    notes += "%s \n" % order.notes
                return notes



            def make_invoice_by_partner(partner, orders, lines_ids):
                """
                    create a new invoice for one supplier
                    @param partner : The object partner
                    @param orders : The set of orders to add in the invoice
                    @param lines : The list of line's id
                """
                name = orders and orders[0].name or ''
                journal_id = account_jrnl_obj.search(cr, uid, [('type', '=', 'purchase')], context=None)
                journal_id = journal_id and journal_id[0] or False
                a = partner.property_account_payable.id
                inv = {
                    'name': name,
                    'origin': name,
                    'type': 'in_invoice',
                    'journal_id':journal_id,
                    'reference' : partner.ref,
                    'account_id': a,
                    'partner_id': partner.id,
                    'invoice_line': [(6,0,lines_ids)],
                    'currency_id' : orders[0].pricelist_id.currency_id.id,
                    'comment': multiple_order_invoice_notes(orders),
                    'payment_term': orders[0].payment_term_id.id,
                    'fiscal_position': partner.property_account_position.id
                }
                inv_id = invoice_obj.create(cr, uid, inv)
                for order in orders:
                    order.write({'invoice_ids': [(4, inv_id)]})
                return inv_id

            for line in purchase_line_obj.browse(cr, uid, record_ids, context=context):
                if (not line.invoiced) and (line.state not in ('draft', 'cancel')):
                    if not line.partner_id.id in invoices:
                        invoices[line.partner_id.id] = []
                    acc_id = purchase_obj._choose_account_from_po_line(cr, uid, line, context=context)
                    inv_line_data = purchase_obj._prepare_inv_line(cr, uid, acc_id, line, context=context)
                    inv_line_data.update({'origin': line.order_id.name,
                        'company_recl_id': line.order_id.company_id.id})
                    inv_id = invoice_line_obj.create(cr, uid, inv_line_data, context=context)
                    purchase_line_obj.write(cr, uid, [line.id], {'invoiced': True, 'invoice_lines': [(4, inv_id)]})
                    invoices[line.partner_id.id].append((line,inv_id))


            res = []
            for result in invoices.values():
                il = map(lambda x: x[1], result)
                orders = list(set(map(lambda x : x[0].order_id, result)))

                res.append(make_invoice_by_partner(orders[0].partner_id, orders, il))

        ################# REASIGNACION DE IMPUESTOS ############################
        ##################### RES ID >>>>>>>  res
        account_inv_obj = self.pool.get('account.invoice')
        tax_obj = self.pool.get('account.tax')
        products_list = []
        reclasification_moves = []
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.reclasification:
                ####### RECLASIFICACION POR QUERY SQL ########
                reclasification_lines = []
                for invoice in account_inv_obj.browse(cr, uid, res, context=None):
                    tax_list = []
                    company_id = invoice.company_id.id
                    ########## QUERY ANTERIOR SIN EL CAMPO company_recl_id
                    # cr.execute("""
                    #     select
                    #         account_invoice_line.product_id,
                    #         account_invoice_line.name as description,
                    #         account_invoice_line.price_subtotal as amount,
                    #         account_invoice_line.quantity,
                    #         (select company_id from account_tax where id=account_invoice_line_tax.tax_id)

                    #         from account_invoice_line join account_invoice_line_tax
                    #         on account_invoice_line_tax.invoice_line_id = account_invoice_line.id
                    #          and account_invoice_line.invoice_id=%s

                    #     """ % invoice.id)
                    cr.execute("""
                        select
                            product_id,
                            name as description,
                            price_subtotal as amount,
                            quantity,
                            company_recl_id as company_id

                            from account_invoice_line where invoice_id=%s

                        """ % invoice.id)
                    reclasification_sql = cr.dictfetchall()
                    #################### RECLASIFICACION POR SQL >>>>>>>>>>>  reclasification_sql

                    ########## VALIDANDO PRODUCTOS SELECCIONADOS QUE NO SEAN SERVICIOS ########
                    cr.execute("""
                        select
                         account_invoice_line.id from account_invoice_line join product_template
                         on product_template.id = account_invoice_line.product_id and
                         account_invoice_line.product_id is not null
                         and product_template.type != 'service' and invoice_id=%s
                        """ % invoice.id)
                    cr_res = cr.fetchall()
                    if cr_res:
                        products_list_ids = [x[0] for x in cr_res if x]
                        if products_list_ids:
                            cr.execute("""
                                select name from product_template where id in %s
                                """, (tuple(products_list_ids),))
                            cr_res = cr.fetchall()
                            products_list = [x[0] for x in cr_res if x]
                            if products_list:
                                raise osv.except_osv(_('Error en Lineas de Compra'),
                                                       _('Las Siguientes Lineas no son Servicios o no se tiene Producto: %s \n Desactive el Campo Reclasificacion Automatica de Servicios.' % str(products_list)) )
                    invoice.write({
                                    'reclasification_validate': True,
                                    'reclasification_lines': [(0,0,x) for x in reclasification_sql],
                                    })
                    tax_company = invoice.company_id.id
                    cr.execute("""
                         select product_id from account_invoice_line where invoice_id = %s group by product_id
                        """ % invoice.id)
                    cr_res = cr.fetchall()
                    invoice_line_product_ids = []
                    if cr_res:
                        invoice_line_product_ids = [x[0] for x in cr_res if x]
                    else:
                        invoice_line_product_ids = []
                    for invpr in invoice_line_product_ids:
                        cr.execute("""
                            select
                                 product_supplier_taxes_rel.tax_id
                                 from  product_supplier_taxes_rel join product_product
                                 on product_supplier_taxes_rel.prod_id=product_product.id
                                 and product_product.id =%s
                                 and product_supplier_taxes_rel.tax_id in (select id from
                                 account_tax where company_id=%s)
                            """, (invpr, tax_company))
                        cr_res = cr.fetchall()
                        tax_line_ids_product = [x[0] for x in cr_res]
                        cr.execute("""
                            select id from account_invoice_line
                             where product_id = %s and invoice_id = %s;
                            """,(invpr,invoice.id, ))
                        cr_res = cr.fetchall()
                        invoice_line_ids = [x[0] for x in cr_res]
                        self.pool.get('account.invoice.line').write(
                            cr, uid, invoice_line_ids, {'invoice_line_tax_id': [(6, 0, tax_line_ids_product)]}, context)

                    ############ Forma Sencilla por Codigo Python ###########
                    # ######### invoice number >>>>>>> invoice.number
                    # tax_list = []
                    # company_id = invoice.company_id.id
                    # for line in invoice.invoice_line:
                    #     if line.product_id:
                    #         if line.product_id.type != 'service':
                    #             products_list.append(line.product_id.name)
                    #     else:
                    #         products_list.append(line.name)
                    #     ################ LINE DESCR >>>> line.name
                    #     if line.invoice_line_tax_id:
                    #         if line.product_id:
                    #             tax_company = False
                    #             for tax in line.invoice_line_tax_id:
                    #                 ############# IMPUESTO ID >>>> tax.id
                    #                 tax_list.append(tax.id)
                    #                 tax_company =tax.company_id.id
                    #             reclasification_moves.append({'product_id': line.product_id.id,
                    #                                            'description':line.name,
                    #                                            'amount':line.price_subtotal,
                    #                                            'quantity':line.quantity,
                    #                                            'company_id': tax_company,
                    #                                         })
                    #             xline = (0,0,{
                    #                         'product_id': line.product_id.id,
                    #                         'description':line.name,
                    #                         'amount':line.price_subtotal,
                    #                         'quantity':line.quantity,
                    #                         'company_id': tax_company,
                    #                         })
                    #             reclasification_lines.append(xline)

                    # invoice.write({
                    #                 'reclasification_validate': True,
                    #                 'reclasification_lines': [x for x in reclasification_lines],
                    #                 })

                    # taxes_company = tax_obj.search(cr, uid, [('id','in',tuple(tax_list)),
                    #                                         ('company_id','=',company_id)])
                    ######################### RESULTADO FINAL PARA LA RECLASIFICACION DE FLETE >>>> reclasification_moves

                    # tax_company = invoice.company_id.id
                    # for line in invoice.invoice_line:
                    #     tax_list = []
                    #     if line.product_id:
                    #         for tax in line.product_id.supplier_taxes_id:
                    #             ############# IMPUESTO ID >>>> tax.id
                    #             tax_list.append(tax.id)
                    #     taxes_company = tax_obj.search(cr, uid, [('id','in',tuple(tax_list)),
                    #                                     ('company_id','=',tax_company)])
                    #     ############ TAXES COMPANY >>>> taxes_company
                    #     if taxes_company:
                    #         line.write({'invoice_line_tax_id': [(6, 0, taxes_company)]})
                        ############## LISTADO DE LOS IMPUESTOS >>>>> tax_list
                    ############## IMPUESTOS FINALES DE LA COMPANY PADRE >>>> taxes_company
                    ############### COMPANY >>>>>> company_id
                if products_list:
                    raise osv.except_osv(_('Error en Lineas de Compra'),
                                           _('Las Siguientes Lineas no son Servicios o no se tiene Producto: %s \n Desactive el Campo Reclasificacion Automatica de Servicios.' % str(products_list)) )

        ################ INTERRUPCION DEL FLUJO PYTHON ############################
        # raise osv.except_osv(_('Interrupcion del Flujo!'),
        #                      _('Debugeando el Codigo de Creacion de Factura desde lineas de Compra') )

        return {
            'domain': "[('id','in', ["+','.join(map(str,res))+"])]",
            'name': _('Supplier Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'view_id': False,
            'context': "{'type':'in_invoice', 'journal_type': 'purchase'}",
            'type': 'ir.actions.act_window'
        }
purchase_line_invoice()

################## CUENTAS DE RECLASIFICACION DE GASTO ####################

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
    'reclasification_account': fields.property(
            type='many2one',
            relation='account.account',
            string="Cuenta de Reclasificacion de Gasto",
            help="Esta Cuenta sera utilizada para Poder distirbuir los Gastos de Flete para las Compañias que realicen una Compra."),
    }
product_category()

class product_template(osv.osv):
    _inherit ='product.template'
    _columns = {
    'reclasification_account': fields.property(
            type='many2one',
            relation='account.account',
            string="Cuenta de Reclasificacion de Gasto",
            help="Esta Cuenta sera utilizada para Poder distirbuir los Gastos de Flete para las Compañias que realicen una Compra."),
        }

    _defaults = {
        }


class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit ='account.invoice'
    _columns = {
        'reclasification_validate': fields.boolean('Requiere Reclasificacion'),
        'reclasification_lines': fields.one2many('invoice.reclasification.fleet','invoice_id','Lineas para Reclasificacion'),
        'move_reference_created': fields.char('Referencia de Polizas de Recl.')
        }

    _defaults = {
        }

    ######## RECLASIFICANDO LA POLIZA Y CREANDO MOVIMIENTOS DE RECLASIFICACION ########
    def invoice_validate(self, cr, uid, ids, context=None):
        ############### AQUI SE HARA LA RECLASIFICACION ##################
        result =  super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        reclasification_config = self.pool.get('reclasification.automatic.config')
        reclasification_config_line = self.pool.get('reclasification.automatic.config.line')
        account_move_line = self.pool.get('account.move.line')
        account_move = self.pool.get('account.move')
        reclasification_id = reclasification_config.search(cr, uid, [])
        account_move_line = self.pool.get('account.move.line')
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.move_id and rec.reclasification_validate:
                move_reference_created = str(rec.origin)+' | '+str(rec.number,)
                rec.write({'move_reference_created': move_reference_created,})

                if reclasification_id:
                    reclasification_br = reclasification_config.browse(cr, uid, reclasification_id, context=None)[0]
                else:
                    raise osv.except_osv(_('Error de Configuracion!'),
                                        _('No se tiene Configuracion para la Reclasificacion de Fletes\nContabilidad --> Proveedores --> Reclasificacion de Fletes') )
                move_id = rec.move_id.id
                account_reclasification_ids = [x.account_bridge_shop.id for x in reclasification_br.account_bridge_lines]
                move_line_used = []
                for r_line in rec.reclasification_lines:
                    #### Si la compañia es igual entonces esta no se reclasificara ####
                    # if r_line.company_id.id == rec.company_id.id:
                        # r_line.unlink()
                    if r_line.company_id.id != rec.company_id.id:
                        product_id = r_line.product_id.id
                        quantity = r_line.quantity
                        amount = r_line.amount
                        if not move_line_used:
                            cr.execute("select id from account_move_line where product_id=%s and quantity=%s and move_id=%s and debit=%s limit 1;",(product_id,quantity,move_id,amount))
                            move_line = cr.fetchall()
                            move_line_id = move_line[0][0] if move_line[0][0] != None else False
                            move_line_used.append(move_line_id)
                        else:
                            cr.execute("select id from account_move_line where product_id=%s and quantity=%s and move_id=%s and id not in %s and debit=%s limit 1;",(product_id,quantity,move_id,tuple(move_line_used),amount))
                            move_line = cr.fetchall()
                            if move_line:
                                move_line_id = move_line[0][0] if move_line[0][0] != None else False
                                move_line_used.append(move_line_id)
                            else:
                                move_line_id = False
                            # try:
                            #     move_line_id = move_line[0][0] if move_line[0][0] != None else False
                            #     move_line_used.append(move_line_id)
                            # except:
                            #     move_line_id =  False

                        # cr.execute("select account_bridge_shop from reclasification_automatic_config_line where company_id=%s limit 1" % r_line.company_id.id)
                        # reclasification_line_id = cr.fetchall()
                        reclasification_line_id = reclasification_config_line.search(cr, uid, [('company_id','=',r_line.company_id.id)])
                        if reclasification_line_id:
                            if move_line_id:
                                reclasification_line = reclasification_config_line.browse(cr, uid, reclasification_line_id, context=None)[0]
                                account_reclasification = reclasification_line.account_bridge_shop.id
                                cr.execute("update account_move_line set account_id=%s where id=%s;" % (account_reclasification,move_line_id))
                        else:
                            raise osv.except_osv(_('Error de Configuracion!'),
                                               _('No se tiene Cuenta de Reclasificacion para la Compañia %s en la Configuracion de Reclasificacion.\nConsulte al Administrador del Sistema'  % r_line.company_id.name) )


                            # try:
                            #     move_line_id = move_line[0][0] if move_line[0][0] != None else False
                            #     move_line_used.append(move_line_id)
                            # except:
                            #     move_line_id =  False

                        # if move_line_id:
                        #     reclasification_line_id = reclasification_config_line.search(cr, uid, [('company_id','=',r_line.company_id.id)])
                        #     if reclasification_line_id:
                        #         reclasification_line = reclasification_config_line.browse(cr, uid, reclasification_line_id, context=None)[0]
                        #         account_reclasification = reclasification_line.account_bridge_shop.id
                        #         cr.execute("update account_move_line set account_id=%s where id=%s;" % (account_reclasification,move_line_id))
                        #     else:
                        #         raise osv.except_osv(_('Error de Configuracion!'),
                        #                            _('No se tiene Cuenta de Reclasificacion para la Compañia %s en la Configuracion de Reclasificacion.\nConsulte al Administrador del Sistema'  % r_line.company_id.name) )

                        # account_move_line.write(cr, uid, [move_line_id], {
                        #                                                 'account_id': reclasification_line_id,
                        #                                                 })
                ####### CREANDO LAS POLIZAS DE RECLASIFICACION #######
                property_obj = self.pool.get('ir.property')
                account_obj = self.pool.get('account.account')
                period_obj = self.pool.get('account.period')
                period_name = rec.move_id.period_id.name
                for r_line in rec.reclasification_lines:
                    #### Si la compañia es igual entonces esta no se reclasificara ####
                    # if r_line.company_id.id == rec.company_id.id:
                        # r_line.unlink()
                    if r_line.company_id.id != rec.company_id.id:
                        product_id = r_line.product_id.id
                        quantity = r_line.quantity
                        amount = r_line.amount
                        description = r_line.description
                        company_id = r_line.company_id.id
                        moves = []
                        account_cost_product = False
                        account_reclasification_product = False
                        ###### CUENTA DE COSTO DE VENTA #########
                        res_id = 'product.template,'+str(product_id)
                        cr.execute("select value_reference from ir_property where name='property_account_expense' and res_id=%s and company_id=%s",(res_id,company_id,))
                        account_property = cr.fetchall()
                        account_property = account_property[0][0] if account_property  else False
                        if account_property:
                            account_property = account_property.split(',')
                            account_property_id = int(account_property[-1])
                            account_cost_product = account_property_id
                        else :
                            res_id = 'product.category,'+str(r_line.product_id.categ_id.id)
                            cr.execute("select value_reference from ir_property where name='property_account_expense_categ' and res_id=%s and company_id=%s",(res_id,company_id,))
                            account_property_categ = cr.fetchall()
                            try:
                                account_property_categ = account_property_categ[0][0] if account_property_categ[0][0] != None else False
                            except:
                                account_property_categ = False
                            if account_property_categ:
                                account_property_categ = account_property_categ.split(',')
                                account_property_categ_id = int(account_property_categ[-1])
                                account_cost_product = int(account_property_categ[-1])
                        if not account_cost_product:
                            raise osv.except_osv(_('Error de Configuracion!'),
                                               _('No se tiene Cuenta de Costo de Venta para el Producto %s en la Configuracion Contable del Producto o Categoria.\nConsulte al Administrador del Sistema'  % r_line.product_id.name) )

                        ######## CUENTA DE RECLASIFICACION ##########
                        res_id = 'product.product,'+str(product_id)
                        cr.execute("select value_reference from ir_property where name='reclasification_account' and res_id=%s and company_id=%s",(res_id,company_id,))
                        account_property = cr.fetchall()
                        account_property = account_property[0][0] if account_property  else False
                        if account_property:
                            account_property = account_property.split(',')
                            account_property_id = int(account_property[-1])
                            account_reclasification_product = account_property_id
                        else :
                            res_id = 'product.category,'+str(r_line.product_id.categ_id.id)
                            cr.execute("select value_reference from ir_property where name='reclasification_account' and res_id=%s and company_id=%s",(res_id,company_id,))
                            account_property_categ = cr.fetchall()
                            # account_property_categ = account_property_categ[0][0] if account_property_categ[0][0] != None else False
                            try:
                                account_property_categ = account_property_categ[0][0] if account_property_categ[0][0] != None else False
                            except:
                                account_property_categ = False
                            if account_property_categ:
                                account_property_categ = account_property_categ.split(',')
                                account_property_categ_id = int(account_property_categ[-1])
                                account_reclasification_product = account_property_categ_id
                        if not account_reclasification_product:
                            raise osv.except_osv(_('Error de Configuracion!'),
                                               _('No se tiene Cuenta de Costo de Venta para el Producto %s en la Configuracion Contable del Producto o Categoria.\nConsulte al Administrador del Sistema'  % r_line.product_id.name) )
                        ############# COMPANY >>>>> r_line.company_id.name
                        ############# CUENTAS >>>>> account_cost_product, account_reclasification_product
                        mline = (0,0,{
                            'name': description,
                            'account_id': account_cost_product, ### Cuenta
                            'partner_id': rec.partner_id.id, ## Cuenta de Costo de Venta
                            'debit': amount,
                            'credit': 0.0,
                            'product_id': product_id,
                            'quantity': quantity,
                            })
                        moves.append(mline)
                        #### Cuenta de Gasto de Producto
                        mline2 = (0,0,{
                                'name': description,
                                'account_id': account_reclasification_product, ### Cuenta de Reclasificacion
                                'partner_id': rec.partner_id.id, ## Cliente
                                'debit': 0.0,
                                'credit': amount,
                                'product_id': product_id,
                                'quantity': quantity,
                                })
                        moves.append(mline2)
                        #### CREANDO LA POLIZA #####
                        journal = self.pool.get('account.journal')
                        journal_id = journal.search(cr, uid, [('company_id','=',r_line.company_id.id),('type','=','purchase')])
                        ################################ JOURNAL ID >>>>>>>>> journal_id
                        if not journal_id:
                            raise osv.except_osv(_('Error de Configuracion!'),
                                                 _('No se tiene Diario de Compra para la Compañia %s .\nConsulte al Administrador del Sistema'  % r_line.company_id.name) )
                        ####################### LINEAS FINALES >>>>>>  moves
                        period_id = period_obj.search(cr, uid, [('name','=',period_name),('company_id','=',company_id)])
                        move_vals = {
                                'journal_id': journal_id[0],
                                'ref': rec.origin+' | '+rec.number,
                                'line_id': [x for x in moves],
                                'company_id': r_line.company_id.id,
                                'period_id': period_id[0],
                                }
                        account_move_id = account_move.create(cr, uid, move_vals, context=None)

        ################# INTERRUPCION DEL FLUJO PYTHON ############################
        # raise osv.except_osv(_('Interrupcion del Flujo!'),
                             # _('Debugeando el Codigo de Creacion de Factura desde lineas de Compra') )
        return result

    def action_cancel(self, cr, uid, ids, context=None):
        result = super(account_invoice, self).action_cancel(cr, uid, ids, context)
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.move_reference_created:
                account_move = self.pool.get('account.move')
                move_del_ids = account_move.search(cr, uid, [('ref','=',rec.move_reference_created)])
                if move_del_ids:
                    try:
                        account_move.unlink(cr, uid, move_del_ids, context=None)
                    except:
                        for ac in account_move.browse(cr, uid, move_del_ids, context=None):
                            ac.button_cancel()
                            ac.unlink()

        return result

class invoice_reclasification_fleet(osv.osv):
    _name = 'invoice.reclasification.fleet'
    _description = 'Lineas para Reclasificacion de Flete'
    _rec_name = 'description'
    _columns = {
        'product_id': fields.many2one('product.product','Producto'),
        'description': fields.char('Descripcion', size=256),
        'amount': fields.float('Monto Reclasificacion', digits=(14,4)),
        'quantity': fields.float('Cantidad', digits=(14,4)),
        'company_id': fields.many2one('res.company','Compañia'),
        'invoice_id': fields.many2one('account.invoice', 'ID Referencia'),
    }
    _defaults = {
        }
