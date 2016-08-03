# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 moylop260 - http://www.hesatecnica.com.com/
#    All Rights Reserved.
#    info skype: german_442 email: (german.ponce@hesatecnica.com)
############################################################################
#    Coded by: german_442 email: (german.ponce@hesatecnica.com)
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


import re
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _

# main mako-like expression pattern

class mail_compose_message(osv.TransientModel):
    _name = 'mail.compose.message'
    _inherit = 'mail.compose.message'
    _description = 'Email composition wizard'
    _columns = {
        'attachment_ids': fields.many2many('ir.attachment',
            'mail_compose_message_ir_attachments_rel',
            'wizard_id', 'attachment_id', 'Attachments'),
    }

    def _get_attachment_ids(self, cr, uid, context=None):
        active_id = context and context.get('active_id', False)
        active_ids = context and context.get('active_ids', False)
        active_model = context and context.get('active_model', False) # Active model busca que modelo es en el cual se esta ejecutando el Wizard
        if active_model == 'account.invoice':
            account_invoice_obj = self.pool.get('account.invoice')
#            for rec in account_invoice_obj.browse(cr, uid, active_ids, context=context):
#                print "###################################### reccccccccccccccccccccccccccc", rec.number
            attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=',active_model),('res_id','=',active_ids[0])], context=context)
            return [(6, 0, [x for x in attachment_ids])]
        return True

    _defaults = {
#        'attachment_ids': _get_attachment_ids, ## Esta funcion retorna la vinculacion de Ids de los Archivos adjuntos en La Factura
    }

    def onchange_attachments(self, cr, uid, ids, attachment_ids, model, res_id, context=None):
        res = {
                }
        ir_attachment_obj = self.pool.get('ir.attachment')
        if model == 'account.invoice':
            try:
                attachment_ids = []
                if res_id:
                    account_obj = self.pool.get('account.invoice')
                    for account in account_obj.browse(cr, uid, [res_id], context=None):
                        if account.loaded_attachment_ids:
                            new_attachment_ids = account.loaded_attachment_ids.split(',')
                            res.update({"attachment_ids": [(6, 0, [int(x) for x in new_attachment_ids])]})
                            ### DESMARCAMOS LAS FACTURAS PARA QUE SE PUEDAN ENVIAR INDIVIDUALMENTE
                            invoice_ids = account_obj.search(cr, uid, [('loaded_attachment_ids','=',account.loaded_attachment_ids)], context=context)
                            if invoice_ids:
                                account_obj.write(cr, uid, invoice_ids, {'loaded_attachment_ids':False})
                        else:
                            wizard_facturae = self.pool.get('ir.attachment.facturae.mx')
                            wizard_ids = wizard_facturae.search(cr, uid, [('model_source','=','account.invoice'),('id_source','=',res_id)])
                            if wizard_ids:
                                for wizard in wizard_facturae.browse(cr, uid, wizard_ids, context=None):
                                    if wizard.file_xml_sign.id:
                                        attachment_ids.append(wizard.file_xml_sign.id)
                                    if wizard.file_pdf.id:
                                        attachment_ids.append(wizard.file_pdf.id)
                                    if not wizard.file_pdf.id:
                                        file_xml_sign = wizard.file_xml_sign.name.split('.')[0] if wizard.file_xml_sign.name else ''
                                        if file_xml_sign:
                                            attachment_obj = self.pool.get('ir.attachment')
                                            attachment_pdf_id = attachment_obj.search(cr, uid,[('name','=',file_xml_sign+'.pdf')])
                                            if attachment_pdf_id:
                                                attachment_ids.append(attachment_pdf_id[0])
                            res.update({"attachment_ids": [(6, 0, [x for x in attachment_ids])]})
            except:
                return {'value': res}

        elif model == 'hr.payslip':
            try:
                attachment_ids = []
                if res_id:
                    wizard_facturae = self.pool.get('ir.attachment.facturae.mx')
                    wizard_ids = wizard_facturae.search(cr, uid, [('model_source','=','hr.payslip'),('id_source','=',res_id)])
                    if wizard_ids:
                        for wizard in wizard_facturae.browse(cr, uid, wizard_ids, context=None):
                            if wizard.file_xml_sign.id:
                                attachment_ids.append(wizard.file_xml_sign.id)
                            if wizard.file_pdf.id:
                                attachment_ids.append(wizard.file_pdf.id)
                            if not wizard.file_pdf.id:
                                file_xml_sign = wizard.file_xml_sign.name.split('.')[0] if wizard.file_xml_sign.name else ''
                                if file_xml_sign:
                                    attachment_obj = self.pool.get('ir.attachment')
                                    attachment_pdf_id = attachment_obj.search(cr, uid,[('name','=',file_xml_sign+'.pdf')])
                                    if attachment_pdf_id:
                                        attachment_ids.append(attachment_pdf_id[0])
                res.update({"attachment_ids": [(6, 0, [x for x in attachment_ids])]})
            except:
                return {'value': res}
        return {'value': res} # Los onchange retornan siempre la estructura{"value": {diccionario de valores a actualizar}}

mail_compose_message()