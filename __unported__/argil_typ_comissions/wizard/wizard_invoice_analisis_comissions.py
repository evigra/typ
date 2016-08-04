# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 HESATEC (<http://www.hesatecnica.com>).
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
from datetime import date, datetime, time, timedelta
from openerp import SUPERUSER_ID


class wizard_analisis_comissions(osv.osv_memory):
    _name = 'wizard.analisis.comissions'
    _description = 'Wizard para Generar Calculo de Comisiones ...'
    _columns = {
        'salesman_information_ids':fields.one2many('salesman.comission.lines','salesman_information_id','Select Salesman'),
        'date': fields.datetime('Date', required=True),
        'all_salesman': fields.boolean('All Salesman'),
        'select_salesman': fields.boolean('Select Salesman'),
        'name': fields.char('Description', size=128),
        'date_start': fields.date('Date Start', required=True),
        'date_end': fields.date('Date End', required=True),
    }

    def _get_date_start(self, cr, uid, context=None):
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date_strp = datetime.strptime(date_now, '%Y-%m-%d %H:%M:%S')
        year = date_strp.year
        month = date_strp.month
        day = date_strp.day

        date_revision = date_strp - timedelta(days=15)
        return str(date_revision)

    _defaults = {
        'date': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_end': lambda *a: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_start': _get_date_start,
        'name': 'Calculo de Comisiones de la Fecha: / / a / /',
        }

    def evaluation_comissions(self, cr, uid, ids, context=None):
        
        user_ids = []
        invoice_ids = []
        report_ids = []
        date_start = 0
        date_end = 0
        invoice_obj = self.pool.get('account.invoice')
        users_obj = self.pool.get('res.users')
        invoice_comission_obj = self.pool.get('invoice.comission.report')
        account_move_obj = self.pool.get('account.move')
        account_move_line_obj = self.pool.get('account.move.line')
        invoice_line_obj = self.pool.get('account.invoice.line')
        product_category = self.pool.get('product.category')
        # if not parameters_id:
        #     raise osv.except_osv(
        #                         _('Error!'),
        #                         _('There are no configuration parameters for commissions'))

        ### POR ERRORES EN LA SEGURIDAD DE OPENERP EN ESTAS LINEAS EMULO LA SEGURIDAD DE MI MODULO PARA ELLO EL USUARIO LOGEADO DEBE TENER ACTIVO EL GRUPO DM3 / Manager
        for rec in self.browse(cr, uid, ids, context=context):
            date_start = rec.date_start
            # print "####### FECHA INICIO >>> ", date_start
            date_end = rec.date_end
            # print "####### FECHA FIN >>>> ", date_end

            # account_move_line_ids = account_move_line_obj.search(cr, uid, [('date_created','>=',date_start),('date_created','<=',date_end),('name','!=','/')])
            # if account_move_line_ids:
            #     cr.execute("select name from account_move_line where id IN %s",(tuple(account_move_line_ids),))
            #     move_line_name_cr = cr.fetchall()
            #     move_line_name_list = []
            #     for mv in move_line_name_cr:
            #         string_unicode = mv[0].encode('ascii','ignore')
            #         string_name = str(string_unicode)
            #         move_line_name_list.append(string_name)

                # account_invoice_parent = invoice_obj.search(cr, uid, [('state','not in',('cancel','draft')),('number','in',tuple(move_line_name_list))])
            account_invoice_parent_ids = invoice_obj.search(cr, uid, [('state','in',('paid','open')),('type','=','out_invoice'),('residual','<=',0.0),('date_payment_real','>=',date_start),('date_payment_real','<=',date_end)])
            print "############### ACCOUNT INVOICE PARENT IDS >>>>>>>> ", len(account_invoice_parent_ids)
            if account_invoice_parent_ids:
                # print "############# INVOICE PARENT >>>>> ", account_invoice_parent
                # print "############# INVOICE PARENT IDS >>>>>", account_invoice_parent_ids
                if rec.all_salesman == True:
                    user_ids = users_obj.search(cr, uid, [('generates_commissions','=',True),('active','=',True)])
                    for user in user_ids:
                        user_br = self.pool.get('res.users').browse(cr, uid, user, context=None)
                        report_lines = []
                        ############### NUEVO METODO MAS EFICIENTE ################
                        invoice_line_ids = []
                        invoice_line_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                ('invoice_id.user_id','=',user),
                                                                ('invoice_id.user_reasigned_id','=',False),
                                                                ('invoice_id.date_payment_real','>=',date_start),
                                                                ('invoice_id.date_payment_real','<=',date_end),
                                                                ('invoice_id.type','=','out_invoice'),
                                                                ])
                        ########### REASIGNACION DE FACTURAS ############
                        invoice_reasigned_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                            ('invoice_id.user_reasigned_id','=',user),
                                                                            ('invoice_id.date_payment_real','>=',date_start),
                                                                            ('invoice_id.date_payment_real','<=',date_end),
                                                                            ('invoice_id.type','=','out_invoice'),
                                                                            ])
                        if invoice_reasigned_ids:
                            invoice_line_ids = invoice_line_ids + invoice_reasigned_ids
                        
                        print "########################### INVOICE LINE IDS >>>>>> ", len(invoice_line_ids)
                        ########### METODO ANTERIOR #############
                        amount_acumulate_invoice = 0.0
                        #### COMPARANDO LA PARTE DE LAS COMPAÑIAS PARA EL CALCULO SI SE DEFINEN COMPANYS ENTONCES NO SE TOMA A EL VENDEDOR
                        if user_br.parameters_id.company_nominal_ids:
                            company_ids = [x.id for x in user_br.parameters_id.company_nominal_ids]
                            # print "############## COMPANIAS >>> ", company_ids
                            invoice_ids = invoice_obj.search(cr, uid, [('id','in',tuple(account_invoice_parent_ids)),('company_id','in',tuple(company_ids))])
                        else:
                            invoice_ids = []
                            #invoice_ids = invoice_obj.search(cr, uid, [('user_id','=',user),('id','in',tuple(account_invoice_parent_ids)),('reasigned_sale','=',False)])
                            if invoice_line_ids :
                                #invoice_ids = invoice_obj.search(cr, uid, [('user_id','=',user),('id','in',tuple(account_invoice_parent_ids)),('reasigned_sale','=',False)])
                                cr.execute("select invoice_id from account_invoice_line where id in %s" ,(tuple(invoice_line_ids),))
                                invoice_query = cr.fetchall()
                                invoice_ids = [x[0] for x in invoice_query]
                        # print "############ INVOICE IDS >>>>>>> ", invoice_ids
                        if invoice_ids:
                            invoice_ids = list(set(invoice_ids))
                            comission_nominal_to_apply_global = 0.0
                            for invoice in invoice_obj.browse(cr, uid, invoice_ids, context=context):
                                # date_last_payments = []
                                ########### MONTOS PARA EL CALCULO ############
                                comision_total = 0.0
                                date_invoice_f = invoice.date_invoice
                                amount_invoice_untaxed = invoice.amount_untaxed
                                invoice_lines = []
                                
                                ################### FECHA DE PAGO DE FACTURA #####################
                                # for pagos in invoice.payment_ids:
                                #     date_last_payments.append(pagos.date)
                                # date_last_payments_sorted = sorted(date_last_payments)
                                # last_payment_date = date_last_payments_sorted[-1]
                                last_payment_date = invoice.date_payment_real

                                date_start_f = datetime.strptime(date_invoice_f, '%Y-%m-%d')
                                date_end_f = datetime.strptime(last_payment_date, '%Y-%m-%d')
                                diff_f = date_end_f - date_start_f
                                days_payment = diff_f.days # Esta variable es el resultado de restar la fecha del ultimo pago y la fecha de factura
                                
                                days_vencimiento = 0
                                date_vencimiento = invoice.date_due
                                date_vencimiento_f = datetime.strptime(date_vencimiento, '%Y-%m-%d')
                                if last_payment_date > date_vencimiento:
                                    diff_vencimiento = date_end_f - date_vencimiento_f
                                    days_vencimiento = diff_vencimiento.days
                                for lines in invoice.invoice_line:
                                    if lines.product_id:
                                        # c_name = lines.product_id.categ_id.name
                                        # category_name = c_name.lower()
                                        #### AQUI EMPEZAMOS A COMPARAR LAS CATEGORIAS
                                        subtotal_cost = 0.0
                                        subtotal_line = lines.price_subtotal
                                        margin_percentage = 100
                                        percentage_comission = 0.0
                                        amount_comission = 0.0
                                        if lines.product_id.categ_id:
                                            if lines.product_id.standard_price > 0.0 and subtotal_line > 0.0:
                                                currency_id = invoice.currency_id.id
                                                currency_base = invoice.company_id.currency_id.id
                                                if currency_id == currency_base:
                                                    cr.execute("select rate from res_currency_rate where currency_id=%s and name<= %s order by name desc limit 1", (currency_id, invoice.date_invoice,))
                                                    currency_tc = cr.fetchall()[0][0]

                                                    subtotal_cost = lines.product_id.standard_price * lines.quantity
                                                    # print "####### SUBTOTAL COST >>>>>>> ", subtotal_cost
                                                    subtotal_cost = subtotal_cost*currency_tc
                                                    margin_amount = subtotal_line - subtotal_cost
                                                    # print "####### MARGIN AMOUNT >>>>>>>> ", margin_amount
                                                    margin_percentage = (margin_amount/subtotal_line)*100
                                                else:
                                                    subtotal_cost = lines.product_id.standard_price * lines.quantity
                                                    # print "####### SUBTOTAL COST >>>>>>> ", subtotal_cost
                                                    margin_amount = subtotal_line - subtotal_cost
                                                    # print "####### MARGIN AMOUNT >>>>>>>> ", margin_amount
                                                    margin_percentage = (margin_amount/subtotal_line)*100
                                                for parameter in user_br.parameters_id.nominal_lines_ids:
                                                    category_list = [x.id for x in parameter.product_category_ids]
                                                    category_parent_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                ('parent_id','in',tuple(category_list))
                                                                    ])
                                                    if category_parent_ids:
                                                        category_parent_2_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                                                        ('parent_id','in',tuple(category_parent_ids))
                                                                                                            ])
                                                    category_list = category_list + category_parent_ids + category_parent_2_ids
                                                    # print "############ CATEGORIAS DE PRODUCTOS >>>>>>>>> ", category_list
                                                    category_comparation = lines.product_id.categ_id.id in category_list or lines.product_id.categ_id.parent_id in category_list
                                                    # print "######### MARGEN INICIAL >>>> ", parameter.margin_percentage_initial
                                                    # print "######### MARGEN FINAL >>>> ", parameter.margin_percentage_final
                                                    if category_comparation == True:
                                                        # print "*********** SI ENTRO A LA CATEGORIA CORRECTA "
                                                        if parameter.general == False:
                                                            #### VERIFICANDO EL PLAZO MAXIMO DE DIAS DESPUES DE VENCIDAS PARA LA COMISION
                                                            if days_vencimiento == 0 or parameter.final_day == 0 or days_vencimiento <= parameter.final_day :
                                                                if margin_percentage >= parameter.margin_percentage_initial and margin_percentage <= parameter.margin_percentage_final:
                                                                    # print "############ ESTE PARAMETRO ES EL CORRECTO <<<<< COMISION >>>> ", parameter.percentage
                                                                    percentage_comission = parameter.percentage
                                                                elif parameter.margin_percentage_final == 0.0:
                                                                    if margin_percentage >= parameter.margin_percentage_initial:
                                                                        percentage_comission = parameter.percentage
                                                            #### AQUI PODEMOS APLICAR LOS DESCUENTOS DE COMISION POR VENCIMIENTO DE DIAS DE PLAZO PARA VENCIMIENTOS
                                                            #elif days_vencimiento <= parameter.final_day :
                                                            #### DESCONTAMOS CUANDO SE COBRARON DESPUES DE VENCIDAS PARA REFACCIONES
                                                            elif "REFACC" in lines.product_id.categ_id.complete_name.upper():
                                                                if days_vencimiento >= 30 and days_vencimiento <=45:
                                                                    if margin_percentage >= parameter.margin_percentage_initial and margin_percentage <= parameter.margin_percentage_final:
                                                                        # print "############ ESTE PARAMETRO ES EL CORRECTO <<<<< COMISION >>>> ", parameter.percentage
                                                                        percentage_comission = parameter.percentage
                                                                    elif parameter.margin_percentage_final == 0.0:
                                                                        if margin_percentage >= parameter.margin_percentage_initial:
                                                                            percentage_comission = parameter.percentage
                                                                    percentage_comission = percentage_comission/2

                                                                else:
                                                                    percentage_comission = 0.0
                                                            elif "EQUI" in lines.product_id.categ_id.complete_name.upper():
                                                                if days_vencimiento >= 15 and days_vencimiento <=30:
                                                                    if margin_percentage >= parameter.margin_percentage_initial and margin_percentage <= parameter.margin_percentage_final:
                                                                        # print "############ ESTE PARAMETRO ES EL CORRECTO <<<<< COMISION >>>> ", parameter.percentage
                                                                        percentage_comission = parameter.percentage
                                                                    elif parameter.margin_percentage_final == 0.0:
                                                                        if margin_percentage >= parameter.margin_percentage_initial:
                                                                            percentage_comission = parameter.percentage
                                                                    percentage_comission = percentage_comission/2
                                                                else:
                                                                    percentage_comission = 0.0

                                                    # print "########## PORCENTAJE FINAL PARA APLICAR >>>>> ", percentage_comission
                                                if percentage_comission:
                                                    amount_comission = subtotal_line * (percentage_comission/100)
                                                    currency_id = invoice.currency_id.id
                                                    currency_base = invoice.company_id.currency_id.id
                                                    if currency_id == currency_base:
                                                        cr.execute("select rate from res_currency_rate where currency_id=%s and name<= %s order by name desc limit 1", (currency_id, invoice.date_invoice,))
                                                        currency_tc = cr.fetchall()[0][0]
                                                        amount_comission = amount_comission / currency_tc
                                                        comision_total += amount_comission
                                                    else:
                                                        comision_total += amount_comission
                                        if amount_comission > 0.0:
                                            dline = (0,0,{
                                                'line_id': lines.id,
                                                'product_id': lines.product_id.id,
                                                'subtotal_cost': subtotal_cost,
                                                'subtotal_line': subtotal_line,
                                                'margin_percentage': margin_percentage,
                                                'margin_amount': margin_amount,
                                                'percentage_comission': percentage_comission,
                                                'amount_comission': amount_comission,
                                                'notes': '',
                                                })
                                            invoice_lines.append(dline)
                                
                                amount_acumulate_invoice += amount_invoice_untaxed
                                if invoice.amount_untaxed > 0 and invoice_lines:
                                    # comision_total = amount_invoice_untaxed * (percentage_nominal_to_apply/100)
                                    # comission_nominal_to_apply_global += comision_total
                                    
                                    comission_nominal_to_apply_global = 0.0
                                    x_line = (0,0,{
                                                    'date_invoice': invoice.date_invoice if invoice.date_invoice else "S/F",
                                                    'origin': invoice.origin if invoice.origin else '',
                                                    'comission': comision_total,
                                                    #'percentage': percentage_nominal_to_apply,
                                                    'amount_payment': amount_invoice_untaxed,
                                                    'payment_days': int(days_payment),
                                                    ######
                                                    'invoice_id': invoice.id,
                                                    'partner_id': invoice.partner_id.id,
                                                    'invoice_line_detail_ids': [x for x in invoice_lines]
                                                    })
                                    report_lines.append(x_line)
                        for parameter in user_br.parameters_id.nominal_lines_ids:
                            comision_total = 0.0
                            amount_invoice_untaxed = 0.0
                            if parameter.general == True:
                                ############### EJECUCION DE EL CODIGO PYTHON DE CADA PARAMETRO
                                category_list = [x.id for x in parameter.product_category_ids]
                                category_parent_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                ('parent_id','in',tuple(category_list))
                                                                    ])
                                if category_parent_ids:
                                    category_parent_2_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                                    ('parent_id','in',tuple(category_parent_ids))
                                                                                        ])
                                category_list = category_list + category_parent_ids + category_parent_2_ids
                                salesman_id = user_br.id
                                # print "############# account_invoice_parent_ids>>>>>>>", account_invoice_parent_ids
                                parameter.execute_code(salesman_id, account_invoice_parent_ids, date_start, date_end)
                                temporal_results_nominal = self.pool.get('temporal.results.nominal')
                                total_comission = 0.0
                                cr.execute("select id from temporal_results_nominal where nominal_id = %s order by id desc limit 1 " % parameter.id)
                                temporal_id = cr.fetchall()
                                # print "################### RESULTADO DEL QUERYYYYYYYYYYYYYYY >>>  ", temporal_id
                                
                                # parameters_id = temporal_results_nominal.search(cr, uid, [('nominal_id','=', parameter.id)])
                                # parameters_id.sort()
                                # temporal_id = 0
                                # print "############### PARAMETROS QUE COINCIDEN >>>>>>> ", parameters_id
                                if temporal_id:
                                    temporal_id = temporal_id[0][0]
                                    temporal_br = temporal_results_nominal.browse(cr, uid, temporal_id, context=None)
                                    total_comission = temporal_br.result_python_code
                                    # print "############################## SELF BROWSE RESULT", total_comission

                                ############### FIN #################
                                if temporal_id:                                    
                                    x_line = (0,0,{
                                                'date_invoice': False,
                                                'origin': parameter.detail_comission,
                                                'comission': total_comission,
                                                #'percentage': percentage_nominal_to_apply,
                                                'amount_payment': amount_invoice_untaxed,
                                                'payment_days': 0,
                                                ######
                                                'invoice_id': False,
                                                'partner_id': False,
                                                'invoice_line_detail_ids': False,
                                                })
                                    report_lines.append(x_line)
                        vals = {
                                'date': rec.date,
                                'date_start': rec.date_start,
                                'date_end': rec.date_end,
                                'user_id': user,
                                'notes': rec.name,
                                'report_lines': [x for x in report_lines],
                                'amount_acumulate_invoice': amount_acumulate_invoice,

                                }
                        if report_lines:
                            report_id = invoice_comission_obj.create(cr, SUPERUSER_ID, vals, context=None)
                            report_ids.append(report_id)

                #### SELECCION DE LOS VENDEDORES LA MISMA MONA REVOLCADA
                elif rec.select_salesman:
                    for lines in rec.salesman_information_ids:
                        user_ids.append(lines.user_id.id)
                    if user_ids:
                        for user in user_ids:
                            user_br = self.pool.get('res.users').browse(cr, uid, user, context=None)
                            report_lines = []
                            ############### NUEVO METODO MAS EFICIENTE ################
                            invoice_line_ids = []
                            invoice_line_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                    ('invoice_id.user_id','=',user),
                                                                    ('invoice_id.user_reasigned_id','=',False),
                                                                    ('invoice_id.date_payment_real','>=',date_start),
                                                                    ('invoice_id.date_payment_real','<=',date_end),
                                                                    ('invoice_id.type','=','out_invoice'),
                                                                    ])
                            ########### REASIGNACION DE FACTURAS ############
                            invoice_reasigned_ids = invoice_line_obj.search(cr, SUPERUSER_ID, [
                                                                                ('invoice_id.user_reasigned_id','=',user),
                                                                                ('invoice_id.date_payment_real','>=',date_start),
                                                                                ('invoice_id.date_payment_real','<=',date_end),
                                                                                ('invoice_id.type','=','out_invoice'),
                                                                                ])
                            if invoice_reasigned_ids:
                                invoice_line_ids = invoice_line_ids + invoice_reasigned_ids
                           
                            print "########################### INVOICE LINE IDS >>>>>> ", len(invoice_line_ids)
                            ########### METODO ANTERIOR #############
                            amount_acumulate_invoice = 0.0
                            #### COMPARANDO LA PARTE DE LAS COMPAÑIAS PARA EL CALCULO SI SE DEFINEN COMPANYS ENTONCES NO SE TOMA A EL VENDEDOR
                            if user_br.parameters_id.company_nominal_ids:
                                company_ids = [x.id for x in user_br.parameters_id.company_nominal_ids]
                                # print "############## COMPANIAS >>> ", company_ids
                                invoice_ids = invoice_obj.search(cr, uid, [('id','in',tuple(account_invoice_parent_ids)),('company_id','in',tuple(company_ids))])
                            else:
                                invoice_ids = []
                                #invoice_ids = invoice_obj.search(cr, uid, [('user_id','=',user),('id','in',tuple(account_invoice_parent_ids)),('reasigned_sale','=',False)])
                                if invoice_line_ids :
                                    cr.execute("select invoice_id from account_invoice_line where id in %s" ,(tuple(invoice_line_ids),))
                                    invoice_query = cr.fetchall()
                                    invoice_ids = [x[0] for x in invoice_query]

                            print "######################## NUMERO DE FACTURAS >>>>>>>>>>>>> ", len (invoice_ids)
                            # print "############ INVOICE IDS >>>>>>> ", invoice_ids
                            if invoice_ids:
                                invoice_ids = list(set(invoice_ids))
                                comission_nominal_to_apply_global = 0.0
                                for invoice in invoice_obj.browse(cr, uid, invoice_ids, context=context):
                                    # date_last_payments = []
                                    ########### MONTOS PARA EL CALCULO ############
                                    comision_total = 0.0
                                    date_invoice_f = invoice.date_invoice
                                    amount_invoice_untaxed = invoice.amount_untaxed
                                    invoice_lines = []
                                    
                                    ################### FECHA DE PAGO DE FACTURA #####################
                                    # for pagos in invoice.payment_ids:
                                    #     date_last_payments.append(pagos.date)
                                    # date_last_payments_sorted = sorted(date_last_payments)
                                    # last_payment_date = date_last_payments_sorted[-1]
                                    last_payment_date = invoice.date_payment_real

                                    date_start_f = datetime.strptime(date_invoice_f, '%Y-%m-%d')
                                    date_end_f = datetime.strptime(last_payment_date, '%Y-%m-%d')
                                    diff_f = date_end_f - date_start_f
                                    days_payment = diff_f.days # Esta variable es el resultado de restar la fecha del ultimo pago y la fecha de factura
                                    
                                    days_vencimiento = 0
                                    date_vencimiento = invoice.date_due
                                    date_vencimiento_f = datetime.strptime(date_vencimiento, '%Y-%m-%d')
                                    if last_payment_date > date_vencimiento:
                                        diff_vencimiento = date_end_f - date_vencimiento_f
                                        days_vencimiento = diff_vencimiento.days
                                    for lines in invoice.invoice_line:
                                        if lines.product_id:
                                            # c_name = lines.product_id.categ_id.name
                                            # category_name = c_name.lower()
                                            #### AQUI EMPEZAMOS A COMPARAR LAS CATEGORIAS
                                            subtotal_cost = 0.0
                                            subtotal_line = lines.price_subtotal
                                            margin_percentage = 100
                                            percentage_comission = 0.0
                                            amount_comission = 0.0
                                            if lines.product_id.categ_id:
                                                if lines.product_id.standard_price > 0.0 and subtotal_line > 0.0:
                                                    currency_id = invoice.currency_id.id
                                                    currency_base = invoice.company_id.currency_id.id
                                                    if currency_id == currency_base:
                                                        cr.execute("select rate from res_currency_rate where currency_id=%s and name<= %s order by name desc limit 1", (currency_id, invoice.date_invoice,))
                                                        currency_tc = cr.fetchall()[0][0]

                                                        subtotal_cost = lines.product_id.standard_price * lines.quantity
                                                        # print "####### SUBTOTAL COST >>>>>>> ", subtotal_cost
                                                        subtotal_cost = subtotal_cost*currency_tc
                                                        margin_amount = subtotal_line - subtotal_cost
                                                        # print "####### MARGIN AMOUNT >>>>>>>> ", margin_amount
                                                        margin_percentage = (margin_amount/subtotal_line)*100
                                                    else:
                                                        subtotal_cost = lines.product_id.standard_price * lines.quantity
                                                        # print "####### SUBTOTAL COST >>>>>>> ", subtotal_cost
                                                        margin_amount = subtotal_line - subtotal_cost
                                                        # print "####### MARGIN AMOUNT >>>>>>>> ", margin_amount
                                                        margin_percentage = (margin_amount/subtotal_line)*100
                                                    for parameter in user_br.parameters_id.nominal_lines_ids:
                                                        category_list = [x.id for x in parameter.product_category_ids]
                                                        category_parent_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                    ('parent_id','in',tuple(category_list))
                                                                        ])
                                                        if category_parent_ids:
                                                            category_parent_2_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                                                            ('parent_id','in',tuple(category_parent_ids))
                                                                                                                ])
                                                        category_list = category_list + category_parent_ids + category_parent_2_ids
                                                        # print "############ CATEGORIAS DE PRODUCTOS >>>>>>>>> ", category_list
                                                        category_comparation = lines.product_id.categ_id.id in category_list or lines.product_id.categ_id.parent_id in category_list
                                                        # print "######### MARGEN INICIAL >>>> ", parameter.margin_percentage_initial
                                                        # print "######### MARGEN FINAL >>>> ", parameter.margin_percentage_final
                                                        if category_comparation == True:
                                                            # print "*********** SI ENTRO A LA CATEGORIA CORRECTA "
                                                            if parameter.general == False:
                                                                #### VERIFICANDO EL PLAZO MAXIMO DE DIAS DESPUES DE VENCIDAS PARA LA COMISION
                                                                if days_vencimiento == 0 or parameter.final_day == 0 or days_vencimiento <= parameter.final_day :
                                                                    if margin_percentage >= parameter.margin_percentage_initial and margin_percentage <= parameter.margin_percentage_final:
                                                                        # print "############ ESTE PARAMETRO ES EL CORRECTO <<<<< COMISION >>>> ", parameter.percentage
                                                                        percentage_comission = parameter.percentage
                                                                    elif parameter.margin_percentage_final == 0.0:
                                                                        if margin_percentage >= parameter.margin_percentage_initial:
                                                                            percentage_comission = parameter.percentage
                                                                #### AQUI PODEMOS APLICAR LOS DESCUENTOS DE COMISION POR VENCIMIENTO DE DIAS DE PLAZO PARA VENCIMIENTOS
                                                                #elif days_vencimiento <= parameter.final_day :
                                                                #### DESCONTAMOS CUANDO SE COBRARON DESPUES DE VENCIDAS PARA REFACCIONES
                                                                elif "REFACC" in lines.product_id.categ_id.complete_name.upper():
                                                                    if days_vencimiento >= 30 and days_vencimiento <=45:
                                                                        if margin_percentage >= parameter.margin_percentage_initial and margin_percentage <= parameter.margin_percentage_final:
                                                                            # print "############ ESTE PARAMETRO ES EL CORRECTO <<<<< COMISION >>>> ", parameter.percentage
                                                                            percentage_comission = parameter.percentage
                                                                        elif parameter.margin_percentage_final == 0.0:
                                                                            if margin_percentage >= parameter.margin_percentage_initial:
                                                                                percentage_comission = parameter.percentage
                                                                        percentage_comission = percentage_comission/2

                                                                    else:
                                                                        percentage_comission = 0.0
                                                                elif "EQUI" in lines.product_id.categ_id.complete_name.upper():
                                                                    if days_vencimiento >= 15 and days_vencimiento <=30:
                                                                        if margin_percentage >= parameter.margin_percentage_initial and margin_percentage <= parameter.margin_percentage_final:
                                                                            # print "############ ESTE PARAMETRO ES EL CORRECTO <<<<< COMISION >>>> ", parameter.percentage
                                                                            percentage_comission = parameter.percentage
                                                                        elif parameter.margin_percentage_final == 0.0:
                                                                            if margin_percentage >= parameter.margin_percentage_initial:
                                                                                percentage_comission = parameter.percentage
                                                                        percentage_comission = percentage_comission/2
                                                                    else:
                                                                        percentage_comission = 0.0

                                                        # print "########## PORCENTAJE FINAL PARA APLICAR >>>>> ", percentage_comission
                                                    if percentage_comission:
                                                        amount_comission = subtotal_line * (percentage_comission/100)
                                                        comision_total += amount_comission
                                            if amount_comission > 0.0:
                                                dline = (0,0,{
                                                    'line_id': lines.id,
                                                    'product_id': lines.product_id.id,
                                                    'subtotal_cost': subtotal_cost,
                                                    'subtotal_line': subtotal_line,
                                                    'margin_percentage': margin_percentage,
                                                    'margin_amount': margin_amount,
                                                    'percentage_comission': percentage_comission,
                                                    'amount_comission': amount_comission,
                                                    'notes': '',
                                                    })
                                                invoice_lines.append(dline)
                                    
                                    amount_acumulate_invoice += amount_invoice_untaxed
                                    if invoice.amount_untaxed > 0 and invoice_lines:
                                        # comision_total = amount_invoice_untaxed * (percentage_nominal_to_apply/100)
                                        # comission_nominal_to_apply_global += comision_total
                                        
                                        comission_nominal_to_apply_global = 0.0
                                        x_line = (0,0,{
                                                        'date_invoice': invoice.date_invoice if invoice.date_invoice else "S/F",
                                                        'origin': invoice.origin if invoice.origin else '',
                                                        'comission': comision_total,
                                                        #'percentage': percentage_nominal_to_apply,
                                                        'amount_payment': amount_invoice_untaxed,
                                                        'payment_days': int(days_payment),
                                                        ######
                                                        'invoice_id': invoice.id,
                                                        'partner_id': invoice.partner_id.id,
                                                        'invoice_line_detail_ids': [x for x in invoice_lines]
                                                        })
                                        report_lines.append(x_line)
                            for parameter in user_br.parameters_id.nominal_lines_ids:
                                comision_total = 0.0
                                amount_invoice_untaxed = 0.0
                                if parameter.general == True:
                                    ############### EJECUCION DE EL CODIGO PYTHON DE CADA PARAMETRO
                                    category_list = [x.id for x in parameter.product_category_ids]
                                    category_parent_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                    ('parent_id','in',tuple(category_list))
                                                                        ])
                                    if category_parent_ids:
                                        category_parent_2_ids = product_category.search(cr, SUPERUSER_ID, [
                                                                                        ('parent_id','in',tuple(category_parent_ids))
                                                                                            ])
                                    category_list = category_list + category_parent_ids + category_parent_2_ids
                                    salesman_id = user_br.id
                                    # print "############# account_invoice_parent_ids>>>>>>>", account_invoice_parent_ids
                                    parameter.execute_code(salesman_id, account_invoice_parent_ids, date_start, date_end)
                                    temporal_results_nominal = self.pool.get('temporal.results.nominal')
                                    total_comission = 0.0
                                    cr.execute("select id from temporal_results_nominal where nominal_id = %s order by id desc limit 1 " % parameter.id)
                                    temporal_id = cr.fetchall()
                                    # print "################### RESULTADO DEL QUERYYYYYYYYYYYYYYY >>>  ", temporal_id
                                    
                                    # parameters_id = temporal_results_nominal.search(cr, uid, [('nominal_id','=', parameter.id)])
                                    # parameters_id.sort()
                                    # temporal_id = 0
                                    # print "############### PARAMETROS QUE COINCIDEN >>>>>>> ", parameters_id
                                    if temporal_id:
                                        temporal_id = temporal_id[0][0]
                                        temporal_br = temporal_results_nominal.browse(cr, uid, temporal_id, context=None)
                                        total_comission = temporal_br.result_python_code
                                        # print "############################## SELF BROWSE RESULT", total_comission
                                    ############### FIN #################
                                    if temporal_id:                                    
                                        x_line = (0,0,{
                                                    'date_invoice': False,
                                                    'origin': parameter.detail_comission,
                                                    'comission': total_comission,
                                                    #'percentage': percentage_nominal_to_apply,
                                                    'amount_payment': amount_invoice_untaxed,
                                                    'payment_days': 0,
                                                    ######
                                                    'invoice_id': False,
                                                    'partner_id': False,
                                                    'invoice_line_detail_ids': False,
                                                    })
                                        report_lines.append(x_line)
                            vals = {
                                    'date': rec.date,
                                    'date_start': rec.date_start,
                                    'date_end': rec.date_end,
                                    'user_id': user,
                                    'notes': rec.name,
                                    'report_lines': [x for x in report_lines],
                                    'amount_acumulate_invoice': amount_acumulate_invoice,

                                    }
                            if report_lines:
                                report_id = invoice_comission_obj.create(cr, SUPERUSER_ID, vals, context=None)
                                report_ids.append(report_id)


        return {
                'domain': "[('id','in', ["+','.join(map(str,report_ids))+"])]",
                'name': _('Comisiones por Vendedor'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'invoice.comission.report',
                'view_id': False,
                'type': 'ir.actions.act_window'
                }

wizard_analisis_comissions()

class salesman_comission_lines(osv.osv_memory):
    _name = 'salesman.comission.lines'
    _description = 'Salesman Comissions Lines'
    _rec_name = 'user_id'
    _columns = {
        'salesman_information_id':fields.many2one('wizard.analisis.comissions', 'ID Referencia', ondelete='cascade'),
        'user_id': fields.many2one('res.users', "Salesman", required=True, select=True),
    }

    _defaults = {
#        'pedido': True,
        }
salesman_comission_lines()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
