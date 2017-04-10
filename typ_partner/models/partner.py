# coding: utf-8

from openerp import api, fields, models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _get_sale_pricelist_id(self):
        sale_team = self.env.user.default_section_id
        return sale_team and sale_team.sale_pricelist_id.id

    @api.model
    def _get_purchase_pricelist_id(self):
        sale_team = self.env.user.default_section_id
        return sale_team and sale_team.purchase_pricelist_id.id

    pricelist_ids = fields.Many2many(
        'product.pricelist', 'pricelist_section_rel', 'pricelist_id',
        'partner_id', string="Pricelist's partner",
        help="Choose the Pricelist that partner can see"
    )
    buyer_id = fields.Many2one(
        "res.users", "Buyer", sercheable=True
    )

    @api.model
    def default_get(self, field):
        """Overwrite default_get method to set the pricelist for the new
        partner depending of the user's salesteam which is trying to create
        the partner

        """
        res = super(ResPartner, self).default_get(field)
        res.update({
            'property_product_pricelist':
            self._get_sale_pricelist_id() or None,
            'property_product_pricelist_purchase':
            self._get_purchase_pricelist_id() or None
        })
        return res
