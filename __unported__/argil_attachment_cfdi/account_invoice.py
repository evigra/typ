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
import tempfile
from xml.dom import minidom
import os
import base64
import hashlib
import tempfile
import os
import codecs
from string import zfill

import xml.dom.minidom
from xml.dom import minidom

class account_invoice(osv.osv):
    _inherit ='account.invoice'
    _columns = {

    }
    
    ######### FUNCION QUE IMPRIME UN REPORTE EN JASPER DESDE UN BOTON CON UNA FUNCION EN PYTHON ######################
    def print_facturae_invoice(self, cr, uid, ids, context=None):
        report_ids = False
        report_obj = self.pool.get('ir.attachment.facturae.mx')
        report_ids = report_obj.search(cr, uid, [('model_source','=','account.invoice'),
            ('id_source','=',ids[0])])
        value = {
            'type': 'ir.actions.report.xml',
            'report_name': 'account.invoice.facturae.webkit',
            'datas': {
                        'model' : 'ir.attachment.facturae.mx',
                        'ids'   : report_ids,
                        }
                    }

        return value


    def action_invoice_sent_jasper(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        #self.attachment_invoice(cr, uid, ids, context=None)
        
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'argil_attachment_cfdi', 'email_template_edi_invoice_jasper')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict(context)
        # file_name = ""
        # for rec in self.browse(cr, uid, ids, context=context):
        #     vat = rec.company_emitter_id.address_invoice_parent_company_id.vat.replace('MX','')
        #     if vat:
        #         file_name = vat + '_CFDI_'+str(rec.number)
        #     else:
        #         file_name = "Factura CFDI "+str(rec.number)
        #     rec.write({'sent':True})
        # attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',ids[0])], context=context)
        
        ctx.update({
            'default_model': 'account.invoice',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
#            'attachment_ids': [x for x in attachment_ids],
            })
        
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

account_invoice()


#### HERENCIA DEL MODELO QUE ENVIA Y GENERA LA FACTURACION ELECTRONICA PARA AGREGAR FUNCIONES
#### COMO ENVIAR POR CORREO, ETC, LIGANDOLO AL FLUJO NORMAL
class ir_attachment_facturae_mx(osv.osv):
    _name = 'ir.attachment.facturae.mx'
    _inherit ='ir.attachment.facturae.mx'
    _columns = {
        }

    def action_invoice_sent_jasper(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        #self.attachment_invoice(cr, uid, ids, context=None)
        attachment_obj = self.pool.get('ir.attachment.facturae.mx')
        attach_browse = self.browse(cr, uid, ids, context=None)[0]
        if attach_browse.model_source == 'account.invoice':
            account_obj = self.pool.get('account.invoice')
            factura_id = [attach_browse.id_source]
            if not attach_browse.id_source:
                xml_name = attach_browse.name
                account_obj = self.pool.get('account.invoice')
                factura_name = xml_name.split('_')[-1]
                factura_s = account_obj.search(cr, uid, [('internal_number','=',factura_name)])
                factura_id = factura_s if factura_s else []
                if not factura_id:
                    raise osv.except_osv(_('Error'), _('No se pudo Enviar la Factura No tiene Relacion con el campo invoice_id o el Nombre no corresponde.\n Contacte al Administrador'))

            assert len(factura_id) == 1, 'This option should only be used for a single id at a time.'
            ir_model_data = self.pool.get('ir.model.data')
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'argil_attachment_cfdi', 'email_template_edi_invoice_jasper')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False 
            ctx = dict(context)
            # file_name = ""
            # for rec in account_obj.browse(cr, uid, factura_id, context=context):
            #     vat = rec.company_emitter_id.address_invoice_parent_company_id.vat.replace('MX','')
            #     if vat:
            #         file_name = vat + '_CFDI_'+str(rec.number)
            #     else:
            #         file_name = "Factura CFDI "+str(rec.number)
            # attachment_ids = self.pool.get('ir.attachment').search(cr, uid, [('res_model','=','account.invoice'),('res_id','=',ids[0])], context=context)
            
            ctx.update({
                'default_model': 'account.invoice',
                'default_res_id': factura_id[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_invoice_as_sent': True,
    #            'attachment_ids': [x for x in attachment_ids],
                })
            wf_service = netsvc.LocalService("workflow")
            if attach_browse.state == 'printable':
                wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', ids[0], 'action_send_customer', cr)
            elif attach_browse.state == 'sent_customer':
                wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', ids[0], 'action_send_backup', cr)
            return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
                    }
        elif attach_browse.model_source == 'hr.payslip':
            payslip_obj = self.pool.get('hr.payslip')
            payslip_id = [attach_browse.id_source]
            if not attach_browse.id_source:
                xml_name = attach_browse.name
                payslip_obj = self.pool.get('hr.payslip')
                factura_name = xml_name
                payslip_s = payslip_obj.search(cr, uid, [('number','=',factura_name)])
                payslip_id = payslip_s if payslip_s else []
                if not payslip_id:
                    raise osv.except_osv(_('Error'), _('No se pudo Enviar el CFDI del Empleado, No se tiene Relacion con el campo invoice_id o el Nombre no corresponde.\n Contacte al Administrador'))

            assert len(payslip_id) == 1, 'This option should only be used for a single id at a time.'
            ir_model_data = self.pool.get('ir.model.data')
            try:
                template_id = ir_model_data.get_object_reference(cr, uid, 'argil_attachment_cfdi', 'email_template_edi_payslip_cfdi')[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
            except ValueError:
                compose_form_id = False 
            ctx = dict(context)

            ctx.update({
                'default_model': 'hr.payslip',
                'default_res_id': payslip_id[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_invoice_as_sent': True,
    #            'attachment_ids': [x for x in attachment_ids],
                })
            wf_service = netsvc.LocalService("workflow")
            if attach_browse.state == 'printable':
                wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', ids[0], 'action_send_customer', cr)
            elif attach_browse.state == 'sent_customer':
                wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', ids[0], 'action_send_backup', cr)
            return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
                    }
            # if attach_browse.state == 'printable':
            #     attach_browse.signal_send_customer()
            # elif attach_browse.state == 'sent_customer':
            #     attach_browse.signal_send_backup()
        return  {'type': 'ir.actions.act_window_close'}

    _default = {
        }
ir_attachment_facturae_mx ()

############################### EXTENDIENDO EL hr.payslip PARA AGREGAR LAS REDES SOCIALES ######################################
class hr_payslip(osv.osv):
    _name = 'hr.payslip'
    _inherit = ['mail.thread', 'ir.needaction_mixin', 'hr.payslip']
    _columns = {
    }

hr_payslip()
