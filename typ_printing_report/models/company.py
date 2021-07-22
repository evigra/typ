from odoo import models, fields


class ResCompany(models.Model):

    _inherit = "res.company"

    report_id = fields.Many2one("ir.actions.report", "Label report", domain="[('model','=','product.product')]")
