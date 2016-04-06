# -*- encoding: utf-8 -*-

from openerp.osv import fields, osv, orm
from openerp import SUPERUSER_ID

class account_invoice(osv.osv):
    _name = 'account.invoice'
    _inherit ='account.invoice'
    _columns = {
        }

    ### Asignacion Automatica de Pedimentos
    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).invoice_validate(cr, 
            uid, ids, context=None)
        # print "########### RESULT >>>>>>>> ", res
        return res

    def create_ir_attachment_facturae(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).create_ir_attachment_facturae(cr, 
            uid, ids, context)
        # print "#################### RESULTADO >>>>>>> ", res
        # model_source
        # id_source
        ir_attach_obj = self.pool.get('ir.attachment.facturae.mx')
        attach_facturae_id = ir_attach_obj.search(cr, SUPERUSER_ID,
            [('model_source','=','account.invoice'),
            ('id_source','=',ids[0])])
        # print "######RESULTADO DE CREAR EL ADJUNTO >>>> ", attach_facturae_id
        if attach_facturae_id:
            self_br = self.browse(cr, uid, ids, context=None)[0]
            for attach in ir_attach_obj.browse(cr, SUPERUSER_ID, attach_facturae_id, context=None):
                # print "########### ATTACH NAME ", attach.name
                # wf_service.trg_validate(uid, 'ir.attachment.facturae.mx', attach.id, 'button_confirm', cr)
                # try:
                #     attach.signal_sign()
                #     attach.signal_printable()
                #     attach.signal_send_customer()
                # except:
                attach.signal_sign() # cr, uid, ids, context ejecutamos desde el browse
                attach.signal_printable()

                ########## PROCESO PARA RETORNAR UN MENSAJE #####
                wizard_message = self.pool.get('mail.compose.message')
                ir_model_data = self.pool.get('ir.model.data')
                #### OBTENGO LA REFERENCIA DEL FORMULARIO DE CORREOS
                compose_form_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'mail', 'email_compose_message_wizard_form')[1]
                try:
                    ##### OBTENGO LA REFERENCIA DEL TEMPLATE DE CORREO
                    template_id = ir_model_data.get_object_reference(cr, SUPERUSER_ID, 'argil_attachment_cfdi', 'email_template_edi_invoice_jasper')[1]
                except ValueError:
                    template_id = False
                ctx = {}
                ##### ENVIO DATOS POR DEFECTO MEDIANTE EL CONTEXT
                ctx.update({
                    'default_model': 'account.invoice', # Valores por default en conext se antepone defacult_ + campo
                    'default_res_id': ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'mark_invoice_as_sent': True,
        #            'attachment_ids': [x for x in attachment_ids],
                    })
                ###### RETORNAMOS  EL FORMULARIO DEL MENSAJE CON LOS DATOS POR DEFAULT
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

        return True