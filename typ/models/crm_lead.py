from odoo import fields, models


class CRMLead(models.Model):
    _inherit = "crm.lead"

    product_quotation_id = fields.Many2one(
        'product.template',
        string='Customer',
        help="Product for which a quotation was requested on website")
