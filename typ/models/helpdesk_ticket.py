
from odoo import models, fields


class HelpdeskTicket(models.Model):

    _inherit = 'helpdesk.ticket'

    product_id = fields.Many2one('product.product')
