from odoo import models, fields


class PurchaseOrder(models.Model):

    _inherit = "res.company"

    email_purchase = fields.Char()
