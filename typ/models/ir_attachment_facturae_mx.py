# -*- coding: utf-8 -*-

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
