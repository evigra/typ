# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductPricelist(models.Model):

    _inherit = 'product.pricelist'

    partner_ids = fields.Many2many(
        'res.partner', 'pricelist_section_rel', 'partner_id', 'pricelist_id',
        string="Pricelist's partner",
        help="Choose the Pricelist that partner can see"
    )
