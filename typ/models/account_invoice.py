# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) info@vauxoo.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from odoo import _, api, models

import io
import zipfile
import base64

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        """If this invoice comes from the PoS, send it by e-mail automatically"""
        res = super(AccountInvoice, self).action_invoice_open()
        if 'pos_picking_id' in self.env.context:
            self.send_invoice_mail()
        return res

    @api.model
    def get_human_value(self, field_name, selection_option):
        """Convert technical key to value to show in selection human readable
        for the user.
        :param field_name: selection field name
        :param selection_option: the technical value of actual_state
        :return: string with the value that will be shown in the user
        """
        data = dict(self.fields_get().get(field_name).get('selection'))
        return data.get(selection_option, '')

    def send_invoice_mail(self):
        """Try send the XML and Invoice report by email to customer.
        I is found a problem with this action will be add a new message
        with the error in the invoice."""
        for record in self:
            if not record.partner_id.email:
                record.message_post(
                    subject=_('Error when try send invoice by email'),
                    body=_('<h2>Error when try send invoice by email</h2>'
                           '<hr>Partner have not email. Please set that value.'
                           '</hr>'))
                continue
            message = record.action_invoice_sent()
            mail = self.env['mail.compose.message'].with_context(
                message.get('context', {})).create({})
            tmp = self.env.ref('account.email_template_edi_invoice', False)
            # If not wkhtmltopdf executable of some error in the onchange
            # (for example trying to render the email custom template) the
            # invoice can be signed but not updated the invoice record, this
            # need to be managed more secure, that's why this try.
            data = {}
            errored = False
            try:
                data = mail.onchange_template_id(
                    tmp.id, None, 'account.invoice', record.id).get(
                        'value', {})
            except BaseException as e:
                _logger.info("invoice not sent even if configured. %s")
                data.update({'subject': str(e)})
                errored = True
            mail.write({
                'body': data.get('body', 'Invoice not sent because an '
                                         'error rendering or generating '
                                         'the email'),
                'partner_ids': data.get('partner_ids', []),
                'email_from': data.get('email_from', ''),
                'attachment_ids': data.get('attachment_ids', []),
                'subject': data.get('subject', ''),
            })
            mail.with_context(mark_invoice_as_sent=True).send_mail()
            mail = self.env['mail.mail'].search([
                ('res_id', '=', record.id),
                ('model', '=', record._name),
                ('subject', '=', data.get('subject', ''))], limit=1)
            if not mail or errored:
                continue
            record.write({'sent': False})
            record.message_post(
                subject=_('Error when try send invoice by email'),
                # Validate that mail exists, because the search can return a
                # mails list with some False
                body='<br>'.join(["- " + msg.failure_reason for msg in mail
                                  if msg.failure_reason]))

    def my_invoices_zip(self):
        invoice_xml = self.l10n_mx_edi_retrieve_last_attachment()
        attachment_id = ''
        invoice_pdf = self.retrieve_last_invoice()

        attachments_exists = self.retrieve_invoices_zip()

        if attachments_exists:
            attachment_id = attachments_exists
        elif invoice_xml is not None and invoice_pdf is not None:
            attachment_id = self.create_zip(invoice_xml, invoice_pdf)
        elif invoice_xml is not None and invoice_pdf is None:
            attachment_id = invoice_xml
        else:
            attachment_id = invoice_pdf

        return attachment_id

    def retrieve_invoices(self):
        domain = [
            ('res_id', '=', self.id),
            ('res_model', '=', 'account.invoice'),
            ('mimetype', '=', 'application/pdf'),
            ('name', 'like', '%.pdf')]
        return self.env['ir.attachment'].search(domain)

    def retrieve_last_invoice(self):
        attachment_ids = self.retrieve_invoices()
        return attachment_ids and attachment_ids[0] or None

    def retrieve_invoices_zip(self):
        domain = [
            ('res_id', '=', self.id),
            ('mimetype', '=', 'application/zip')]
        attachments = self.env['ir.attachment'].search(domain)
        return attachments

    def create_zip(self, invoice_xml, invoice_pdf):
        zip_stream = io.BytesIO()
        with zipfile.ZipFile(zip_stream, 'w') as myzip:
            myzip.writestr(invoice_xml.name,
                           base64.b64decode(invoice_xml.datas))
            myzip.writestr(invoice_pdf.name,
                           base64.b64decode(invoice_pdf.datas))
            myzip.close()
            zip_name = invoice_xml.name.replace(".xml", ".zip")
            values = {
                'name': zip_name,
                'type': 'binary',
                'mimetype': 'application/zip',
                'public': False,
                'db_datas': base64.b64encode(zip_stream.getvalue()),
                'res_id': invoice_xml.res_id,
                'datas_fname': zip_name
            }
        attachment_id = self.env['ir.attachment'].create(values)
        return attachment_id

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        """Use the pos order usage and payment method"""
        usage = self.l10n_mx_edi_usage or self.partner_id.l10n_mx_edi_usage
        payment_method = self.l10n_mx_edi_payment_method_id or \
            self.partner_id.l10n_mx_edi_payment_method_id
        res = super()._onchange_partner_id()
        if self._context.get('l10n_mx_edi_avoid_partner_defaults', False):
            self.update({
                'l10n_mx_edi_usage': usage,
                'l10n_mx_edi_payment_method_id': payment_method.id,
            })
        return res
