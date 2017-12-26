# -*- coding: utf-8 -*-

import base64
from lxml import objectify, etree

from openerp import models, fields, api


class IrAttachmentFacturaeMx(models.Model):

    _inherit = "ir.attachment.facturae.mx"

    report_lang = fields.Char(
        'Report Language', compute="_compute_report_lang",
        help="This field is automatically set from partner of account invoice"
        " object")

    @api.depends('partner_id')
    def _compute_report_lang(self):
        for record in self:
            if record.model_source == 'account.invoice':
                invoice = self.env['account.invoice'].browse(self.id_source)
                record.report_lang = invoice.partner_id.lang
            elif record.model_source == 'account.bank.statement.line':
                statement = self.env['account.bank.statement.line'].browse(
                    self.id_source)
                record.report_lang = statement.partner_id.lang

    @api.multi
    def fix_xml_encoding(self):
        """This method is a workaround to fix XML files which were returned
        without encoding attribute after being signed with Vauxoo's PAC. It
        goes through XML files and write the encoding attribute where
        necessary"""
        for attach in self:
            file_signed = attach.file_xml_sign
            xml = objectify.fromstring(base64.decodestring(file_signed.datas))
            xml = etree.tostring(xml, xml_declaration=True, encoding='utf-8')
            file_signed.write({
                'datas': base64.encodestring(
                    xml.decode('UTF-8').encode('UTF-8')),
            })

    @api.multi
    def _get_context_extra_data(self):
        res = super(
            IrAttachmentFacturaeMx, self)._get_context_extra_data()
        for att in self.filtered(
                lambda r: r.id_source and r.model_source in (
                    'account.invoice', 'account.bank.statement.line')):
            model = self.env[att.model_source]
            doc = model.browse(att.id_source)
            partner = doc.partner_id
            partner_address = partner.read([
                'street', 'l10n_mx_street3', 'l10n_mx_street4', 'street2',
                'l10n_mx_city2', 'city', 'state_id', 'zip', 'country_id'])[0]
            partner_address['state_id'] = partner_address.get(
                'state_id') and partner_address.get('state_id')[1]
            partner_address['country_id'] = partner_address.get(
                'country_id') and partner_address.get('country_id')[1]
            res['partner_address'] = partner_address
            issued_address = doc.address_issued_id if att.model_source == 'account.invoice' else {}  # noqa
            if issued_address:
                issued_address = issued_address.read([
                    'street', 'l10n_mx_street3', 'l10n_mx_street4', 'street2',
                    'l10n_mx_city2', 'city', 'state_id', 'zip',
                    'country_id'])[0]
                issued_address['state_id'] = issued_address.get(
                    'state_id') and issued_address.get('state_id')[1]
                issued_address['country_id'] = issued_address.get(
                    'country_id') and issued_address.get('country_id')[1]
            res['issued_address'] = issued_address
        return res
