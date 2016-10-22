# coding: utf-8

from openerp import fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    pricelist_ids = fields.Many2many(
        'product.pricelist', 'pricelist_section_rel', 'pricelist_id',
        'partner_id', string="Pricelist's partner",
        help="Choose the Pricelist that partner can see"
    )

    buyer_id = fields.Many2one("res.users", "Buyer", sercheable=True)
