from odoo import fields, models

# from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP  -> TODO: review on v14.0


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_highlight = fields.Boolean(
        default=False,
        string="Highlight Product",
        help="Manual selector for featured products",
    )
    # TODO: It was split_method in 11.0 then this need to be reviewed
    split_method_landed_cost = fields.Selection(default="by_current_cost_price")

    # @api.model  # TODO: Reimplement this with core feature.
    # def _get_price_taxed(self, untaxed_price):
    #     self.ensure_one()
    #     taxes = []
    #     for tax in self.taxes_id:
    #         taxes += (tax.sudo().compute_all(untaxed_price, currency=None, quantity=1.0,
    # product=self, partner=None, ) .get("taxes") )
    #     taxed_price = sum([tax.get("amount") for tax in taxes]) + untaxed_price
    #     return taxed_price

    # def is_favorite(self):  # TODO: Reimplement this with the core feature
    #     self.ensure_one()
    #     result_wish = self.env["user.wishlist"].search(
    #         [
    #             ("product_template_id", "=", self.id),
    #             ("user_id", "=", self.env.uid),
    #         ],
    #         limit=1,
    #     )
    #     return bool(result_wish)

    # TODO: review in 14.0
    # def price_compute(self, price_type, uom=False, currency=False,
    #                   company=False):
    #     if self.env.context.get('other_pricelist'):
    #         return 0
    #     return super(ProductTemplate, self).price_compute(
    #         price_type, uom=uom, currency=currency, company=company)
