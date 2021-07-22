from odoo import api, fields, models


class PurchaseOrder(models.Model):
    
    _inherit = "purchase.order"

    sale_order_id = fields.Many2one("sale.order", "Sale Order", help="Reference to Sale Order")
    supply_commitment_date = fields.Date(
        states={"cancel": [("readonly", True)], "done": [("readonly", True)], "purchase": [("readonly", True)]},
        help="Date that the supplier undertakes to deliver.",
        copy=False,
    )

    @api.model
    def _prepare_picking(self):
        res = super()._prepare_picking()
        if self.origin:
            new_origin = self.origin + ":" + self.name
            res.update({"origin": new_origin})
        return res
