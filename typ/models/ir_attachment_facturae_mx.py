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
            if record.model_source != 'account.invoice':
                continue
            invoice = self.env['account.invoice'].browse(self.id_source)
            record.report_lang = invoice.partner_id.lang

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
