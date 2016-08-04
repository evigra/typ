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
from datetime import timedelta
import time
import os

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit ='account.invoice'
    _columns = {
        }

    _defaults = {
        }
        
    # def write(self, cr, uid, ids, vals, context=None):
    #     self_br = self.browse(cr, uid, ids, context=None)[0]
    #     company_id = self_br.company_id.id
    #     if 'invoice_datetime' in vals:
    #         invoice_datetime = vals['invoice_datetime']
    #         # invoice_obj = self.pool.get('account.invoice')
    #         # invoice_id = account_invoice.search(cr, uid, [('id','!=',ids[0]),('invoice_datetime','=',)])
    #         #vals.update({'asn':add_n+asn})
    #         if invoice_datetime != False:
    #             cr.execute("""select id from account_invoice where id != %s and invoice_datetime = '%s' and company_id = %s;""" % (ids[0], invoice_datetime, company_id,))
    #             invoice_ids = cr.fetchall()
    #             if invoice_ids:
    #                 date_strp = datetime.datetime.strptime(invoice_datetime, '%Y-%m-%d %H:%M:%S')
    #                 invoice_datetime_new = date_strp + timedelta(minutes=1,seconds=12)
    #                 invoice_datetime_new = str(invoice_datetime_new)
                    
    #                 cr.execute("""select id from account_invoice where id != %s and invoice_datetime = '%s' and company_id = %s;""" % (ids[0], invoice_datetime_new, company_id,))
    #                 invoice_ids = cr.fetchall()
    #                 while (invoice_ids != []):
    #                     date_strp = datetime.datetime.strptime(invoice_datetime, '%Y-%m-%d %H:%M:%S')
    #                     invoice_datetime_new = date_strp + timedelta(minutes=1,seconds=12)
    #                     invoice_datetime_new = str(invoice_datetime_new)
    #                     cr.execute("""select id from account_invoice where id != %s and invoice_datetime = '%s' and company_id = %s;""" % (ids[0], invoice_datetime_new, company_id,))
    #                     invoice_ids = cr.fetchall()
    #                 vals.update({'invoice_datetime':invoice_datetime_new})
    #     result = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
    #     return result

    def fecha_actual_gtm6(self,):
        date_facturae = time.strftime('%Y-%m-%d %H:%M:%S')
        date_facturae_srtp = datetime.datetime.strptime(date_facturae, '%Y-%m-%d %H:%M:%S')
        date_facturae_6 = date_facturae_srtp - timedelta(hours=6)
        date_facturae_6 = date_facturae_6.strftime('%Y-%m-%d %H:%M:%S')
        return date_facturae_6

    def fecha_actual_gtm6_plus(self, fecha):
        date_facturae_srtp = datetime.datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        date_facturae_6 = date_facturae_srtp - timedelta(hours=6)
        date_facturae_6 = date_facturae_6.strftime('%Y-%m-%d %H:%M:%S')
        return date_facturae_6

    def assigned_datetime(self, cr, uid, values, context=None):
        if context is None:
            context = {}
        res = {}
        user_br = self.pool.get('res.users').browse(cr, uid, uid, context=None)
        company_id = user_br.company_id.id
        if values.get('date_invoice', False) and\
                                    not values.get('invoice_datetime', False):
                                    
            user_hour = self._get_time_zone(cr, uid, [], context=context)
            time_invoice = datetime.time(abs(user_hour), 0, 0)

            date_invoice = datetime.datetime.strptime(
                values['date_invoice'], '%Y-%m-%d').date()
                
            dt_invoice = datetime.datetime.combine(
                date_invoice, time_invoice).strftime('%Y-%m-%d %H:%M:%S')

            res['invoice_datetime'] = dt_invoice
            res['date_invoice'] = values['date_invoice']
            
        if values.get('invoice_datetime', False) and not\
            values.get('date_invoice', False):
            date_invoice = fields.datetime.context_timestamp(cr, uid,
                datetime.datetime.strptime(values['invoice_datetime'],
                tools.DEFAULT_SERVER_DATETIME_FORMAT), context=context)
            res['date_invoice'] = date_invoice
            res['invoice_datetime'] = values['invoice_datetime']
        
        if 'invoice_datetime' in values  and 'date_invoice' in values:
            if values['invoice_datetime'] and values['date_invoice']:
                date_inv = values['date_invoice']
                res['date_invoice'] = date_inv
                res['invoice_datetime'] = date_inv
                # date_invoice = datetime.datetime.strptime(
                #     values['invoice_datetime'],
                #     '%Y-%m-%d %H:%M:%S').date().strftime('%Y-%m-%d')
                # if date_invoice != values['date_invoice']:
                #     raise osv.except_osv(_('Warning!'),
                #             _('Invoice dates should be equal'))
                            
        if  not values.get('invoice_datetime', False) and\
                                        not values.get('date_invoice', False):
            res['date_invoice'] = fields.date.context_today(self,cr,uid,context=context)
            res['invoice_datetime'] = fields.datetime.now()

        ##### CORRECCION DE LA FECHA HORA #####

        res['invoice_datetime'] = fields.datetime.now()

        date_final = fields.datetime.now()
        cr.execute("""select id from account_invoice where invoice_datetime = '%s' and company_id = %s;""" % (date_final, company_id,))
        invoice_ids = cr.fetchall()
        if invoice_ids:
            invoice_datetime_new = ''
            while (invoice_ids != []):
                date_strp = datetime.datetime.strptime(date_final, '%Y-%m-%d %H:%M:%S')
                invoice_datetime_new = date_strp + timedelta(seconds=15)
                invoice_datetime_new = str(invoice_datetime_new)
                cr.execute("""select id from account_invoice where  invoice_datetime = '%s' and company_id = %s;""" % (invoice_datetime_new, company_id,))
                invoice_ids = cr.fetchall()
            if invoice_datetime_new:
                res.update({'invoice_datetime':invoice_datetime_new})
            else:
                res['invoice_datetime'] = fields.datetime.now()

        return res

    def action_cancel(self, cr, uid, ids, context=None):
        result = super(account_invoice, self).action_cancel(cr, uid, ids, context)
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.date_invoice:
                date_now = datetime.datetime.now().strftime('%Y-%m-%d')
                date_now_split = date_now.split('-')
                date_invoice = rec.date_invoice
                date_invoice_split = date_invoice.split('-')

                if date_now_split[0:2] != date_invoice_split[0:2]:
                    if rec.move_id:
                        move_id = rec.move_id.id
                        cr.execute("update account_invoice set move_id=null where id=%s ;" % rec.id)
                        cr.execute("delete from account_move where id=%s ;" % move_id)
                        if rec.move_id:
                            raise osv.except_osv(
                                    _('Error !'),
                                    _('No puede Cancelar una Factura en un Periodo Distinto al Acutal.\nPrimero Elimine el Asiento Contable!!!'))
                    
        return result

    def remove_account_move_inv(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=None):
            if rec.move_id:
                move_id = rec.move_id.id
                cr.execute("update account_invoice set move_id=null where id=%s ;" % rec.id)
                cr.execute("delete from account_move where id=%s ;" % move_id)
                rec.action_cancel()

        return True


class ir_attachment_facturae_mx(osv.osv):
    _name = 'ir.attachment.facturae.mx'
    _inherit ='ir.attachment.facturae.mx'

    # model_source
    # id_source

    def _get_invoice(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.model_source == 'account.invoice':
                if rec.id_source:
                    res[rec.id] = int(rec.id_source)
        return res

    _columns = {
        'invoice_source_id': fields.function(_get_invoice, string="Factura", method=True, type='many2one', relation="account.invoice"),

        }

    _defaults = {
        }

    def signal_sign(self, cr, uid, ids, context=None):
        res = super(ir_attachment_facturae_mx, self).signal_sign(cr, uid, ids, context)
        for rec in self.browse(cr, uid, ids, context=None):
            date_invoice = rec.invoice_source_id.date_invoice
            date_facturae = rec.invoice_source_id.invoice_datetime

            date_strp = datetime.datetime.strptime(date_facturae, '%Y-%m-%d %H:%M:%S')
            date_facturae_72_hours = date_strp - timedelta(hours=72)
            date_facturae_72_hours = str(date_facturae_72_hours)
            if date_invoice >= date_facturae_72_hours:
                return res
            raise osv.except_osv(_('Error!'), 
                _('El tiempo máximo que se tiene a partir de que se genera el CFDI y el momento de enviarlo para hacer el timbrado es de 72 horas.\
                 \nModifique la Factura y Actualice el Campo Fecha de Factura.\nSi piensa que esto es un Error: Consulte al Administrador del Sistema.'))

        return res


# ###### REVISAR LA SIGUIENTE EXPRESION #########
# class account_move_line(osv.osv):
#     _name = 'account.move.line'
#     _inherit ='account.move.line'
#     _columns = {
#         }

#     _defaults = {
#         }


#     def create(self, cr, uid, vals, context=None, check=True):
#         account_obj = self.pool.get('account.account')
#         tax_obj = self.pool.get('account.tax')
#         move_obj = self.pool.get('account.move')
#         cur_obj = self.pool.get('res.currency')
#         journal_obj = self.pool.get('account.journal')
#         context = dict(context or {})
#         if vals.get('move_id', False):
#             move = self.pool.get('account.move').browse(cr, uid, vals['move_id'], context=context)
#             if move.company_id:
#                 vals['company_id'] = move.company_id.id
#             if move.date and not vals.get('date'):
#                 vals['date'] = move.date
#         if ('account_id' in vals) and not account_obj.read(cr, uid, [vals['account_id']], ['active'])[0]['active']:
#             raise osv.except_osv(_('Bad Account!'), _('You cannot use an inactive account.'))
#         if 'journal_id' in vals and vals['journal_id']:
#             context['journal_id'] = vals['journal_id']
#         if 'period_id' in vals and vals['period_id']:
#             context['period_id'] = vals['period_id']
#         if ('journal_id' not in context) and ('move_id' in vals) and vals['move_id']:
#             m = move_obj.browse(cr, uid, vals['move_id'])
#             context['journal_id'] = m.journal_id.id
#             context['period_id'] = m.period_id.id
#         #we need to treat the case where a value is given in the context for period_id as a string
#         if 'period_id' in context and not isinstance(context.get('period_id', ''), (int, long)):
#             period_candidate_ids = self.pool.get('account.period').name_search(cr, uid, name=context.get('period_id',''))
#             if len(period_candidate_ids) != 1:
#                 raise osv.except_osv(_('Error!'), _('No period found or more than one period found for the given date.'))
#             context['period_id'] = period_candidate_ids[0][0]
#         if not context.get('journal_id', False) and context.get('search_default_journal_id', False):
#             context['journal_id'] = context.get('search_default_journal_id')
#         self._update_journal_check(cr, uid, context['journal_id'], context['period_id'], context)
#         move_id = vals.get('move_id', False)
#         journal = journal_obj.browse(cr, uid, context['journal_id'], context=context)
#         vals['journal_id'] = vals.get('journal_id') or context.get('journal_id')
#         vals['period_id'] = vals.get('period_id') or context.get('period_id')
#         vals['date'] = vals.get('date') or context.get('date')
#         if not move_id:
#             if journal.centralisation:
#                 #Check for centralisation
#                 res = self._check_moves(cr, uid, context)
#                 if res:
#                     vals['move_id'] = res[0]
#             if not vals.get('move_id', False):
#                 if journal.sequence_id:
#                     #name = self.pool.get('ir.sequence').next_by_id(cr, uid, journal.sequence_id.id)
#                     v = {
#                         'date': vals.get('date', time.strftime('%Y-%m-%d')),
#                         'period_id': context['period_id'],
#                         'journal_id': context['journal_id']
#                     }
#                     if vals.get('ref', ''):
#                         v.update({'ref': vals['ref']})
#                     move_id = move_obj.create(cr, uid, v, context)
#                     vals['move_id'] = move_id
#                 else:
#                     raise osv.except_osv(_('No Piece Number!'), _('Cannot create an automatic sequence for this piece.\nPut a sequence in the journal definition for automatic numbering or create a sequence manually for this piece.'))
#         ok = not (journal.type_control_ids or journal.account_control_ids)
#         if ('account_id' in vals):
#             account = account_obj.browse(cr, uid, vals['account_id'], context=context)
#             if journal.type_control_ids:
#                 type = account.user_type
#                 for t in journal.type_control_ids:
#                     if type.code == t.code:
#                         ok = True
#                         break
#             if journal.account_control_ids and not ok:
#                 for a in journal.account_control_ids:
#                     if a.id == vals['account_id']:
#                         ok = True
#                         break
#             # Automatically convert in the account's secondary currency if there is one and
#             # the provided values were not already multi-currency
#             if account.currency_id and 'amount_currency' not in vals and account.currency_id.id != account.company_id.currency_id.id:
#                 vals['currency_id'] = account.currency_id.id
#                 ctx = {}
#                 if 'date' in vals:
#                     ctx['date'] = vals['date']
#                 vals['amount_currency'] = cur_obj.compute(cr, uid, account.company_id.currency_id.id,
#                     account.currency_id.id, vals.get('debit', 0.0)-vals.get('credit', 0.0), context=ctx)
#         if not ok:
#             raise osv.except_osv(_('Bad Account!'), _('You cannot use this general account in this journal, check the tab \'Entry Controls\' on the related journal.'))

#         # amount_crr = vals['amount_currency']
#         # vals['amount_currency'] = (amount_crr)* -1
        
#         ################## CHERMAN TRATANDO DE ARREGLAR EL AMOUNT_CURRENCY EN NOTAS DE CREDITO
#         currency_mxn  = self.pool.get('res.currency'). search(cr, uid, [('name','=','MXN')])
#         if 'credit' in vals:
#             print "############### ENTRO ACA >>>>>>>>>> "
#             if vals['credit'] > 0.0:
#                 if 'amount_currency' in vals:
#                     if vals['amount_currency'] > 0.0:
#                         if 'currency_id' in vals:
#                             if vals['currency_id'] != currency_mxn[0]:
#                                 amount_crr = vals['amount_currency']
#                                 vals['amount_currency'] = (amount_crr)* -1
#         ##################### FIN ########################
#         result = super(account_move_line, self).create(cr, uid, vals, context=context)
#         # CREATE Taxes
#         if vals.get('account_tax_id', False):
#             tax_id = tax_obj.browse(cr, uid, vals['account_tax_id'])
#             total = vals['debit'] - vals['credit']
#             base_code = 'base_code_id'
#             tax_code = 'tax_code_id'
#             account_id = 'account_collected_id'
#             base_sign = 'base_sign'
#             tax_sign = 'tax_sign'
#             if journal.type in ('purchase_refund', 'sale_refund') or (journal.type in ('cash', 'bank') and total < 0):
#                 base_code = 'ref_base_code_id'
#                 tax_code = 'ref_tax_code_id'
#                 account_id = 'account_paid_id'
#                 base_sign = 'ref_base_sign'
#                 tax_sign = 'ref_tax_sign'
#             base_adjusted = False
#             for tax in tax_obj.compute_all(cr, uid, [tax_id], total, 1.00, force_excluded=False).get('taxes'):
#                 #create the base movement
#                 if base_adjusted == False:
#                     base_adjusted = True
#                     if tax_id.price_include:
#                         total = tax['price_unit']
#                     newvals = {
#                         'tax_code_id': tax[base_code],
#                         'tax_amount': tax[base_sign] * abs(total),
#                     }
#                     if tax_id.price_include:
#                         if tax['price_unit'] < 0:
#                             newvals['credit'] = abs(tax['price_unit'])
#                         else:
#                             newvals['debit'] = tax['price_unit']
#                     self.write(cr, uid, [result], newvals, context=context)
#                 else:
#                     data = {
#                         'move_id': vals['move_id'],
#                         'name': tools.ustr(vals['name'] or '') + ' ' + tools.ustr(tax['name'] or ''),
#                         'date': vals['date'],
#                         'partner_id': vals.get('partner_id', False),
#                         'ref': vals.get('ref', False),
#                         'statement_id': vals.get('statement_id', False),
#                         'account_tax_id': False,
#                         'tax_code_id': tax[base_code],
#                         'tax_amount': tax[base_sign] * abs(total),
#                         'account_id': vals['account_id'],
#                         'credit': 0.0,
#                         'debit': 0.0,
#                     }
#                     self.create(cr, uid, data, context)
#                 #create the Tax movement
#                 if not tax['amount'] and not tax[tax_code]:
#                     continue
#                 data = {
#                     'move_id': vals['move_id'],
#                     'name': tools.ustr(vals['name'] or '') + ' ' + tools.ustr(tax['name'] or ''),
#                     'date': vals['date'],
#                     'partner_id': vals.get('partner_id',False),
#                     'ref': vals.get('ref',False),
#                     'statement_id': vals.get('statement_id', False),
#                     'account_tax_id': False,
#                     'tax_code_id': tax[tax_code],
#                     'tax_amount': tax[tax_sign] * abs(tax['amount']),
#                     'account_id': tax[account_id] or vals['account_id'],
#                     'credit': tax['amount']<0 and -tax['amount'] or 0.0,
#                     'debit': tax['amount']>0 and tax['amount'] or 0.0,
#                 }
#                 self.create(cr, uid, data, context)
#             del vals['account_tax_id']

#         recompute = journal.env.recompute and context.get('recompute', True)
#         if check and not context.get('novalidate') and (recompute or journal.entry_posted):
#             tmp = move_obj.validate(cr, uid, [vals['move_id']], context)
#             if journal.entry_posted and tmp:
#                 move_obj.button_validate(cr,uid, [vals['move_id']], context)
#         return result
