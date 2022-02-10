from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    partner_ids = fields.Many2many(
        "res.partner",
        "partner_pricelist_rel",
        "pricelist_id",
        "partner_id",
        string="Pricelist's partner",
        help="Choose the Pricelist that partner can see",
    )

    def _get_partner_pricelist_multi(self, partner_ids, company_id=None):
        """Define new priority when determining applicable pricelist

        The new priority is as follows:
        - Pricelist set on the partner
        - Pricelist set on current user's sales team
        - Fallback to default beavior (generic property, country group, etc)
        """
        # 1. Check pricelist set on the partner (ir.property)
        company_id = company_id or self.env.company.id
        result = (
            self.env["ir.property"]
            .with_company(company_id)
            ._get_multi("property_product_pricelist", "res.partner", partner_ids)
        )

        # 2. Take pricelist from sales team
        remaining_partner_ids = [
            pid for pid, val in result.items() if not val or not val._get_partner_pricelist_multi_filter_hook()
        ]
        pricelist_on_team = self.env.user.sale_team_id.sale_pricelist_id
        result.update({partner_id: pricelist_on_team for partner_id in remaining_partner_ids})

        # 3. Fallback to default behavior
        remaining_partner_ids = [pid for pid in remaining_partner_ids if not result[pid]]
        result.update(super()._get_partner_pricelist_multi(remaining_partner_ids, company_id))
        return result

    def _get_nested_pricelists(self):
        """Get all pricelists related to this one, i.e. nested ones"""
        related_pricelists = self.with_context(prefetch_fields=False)
        while related_pricelists.item_ids.base_pricelist_id - related_pricelists:
            related_pricelists |= related_pricelists.item_ids.base_pricelist_id
        return related_pricelists

    def _query_price_rule_get_items(self):
        """Order pricelist items by sequence also when they're retrieved by SQL"""
        query = super()._query_price_rule_get_items()
        query = query.replace("item.applied_on", "item.sequence, item.applied_on")
        return query
