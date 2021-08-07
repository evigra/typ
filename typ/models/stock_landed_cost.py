from odoo import api, fields, models


class StockLandedCost(models.Model):
    _inherit = "stock.landed.cost"

    move_ids = fields.Many2many(
        "stock.move",
        "stock_landed_move_rel",
        "stock_landed_cost_id",
        "move_id",
        domain=[("state", "in", ("done",))],
    )
    invoice_ids = fields.One2many("account.move", "stock_landed_cost_id")
    guide_ids = fields.One2many(
        "stock.landed.cost.guide",
        "landed_cost_id",
        string="Guides",
        help="Guides which contain items to be used as landed costs",
        domain="[('state', '!=', 'draft')]",
    )
    port_input = fields.Selection(
        selection=[
            ("nog", "NOGALES"),
            ("san", "SAN DIEGO"),
            ("cxl", "CALEXICO"),
            ("ese", "ENSENADA"),
            ("zlo", "MANZANILLO"),
            ("lrd", "LAREDO"),
            ("nac", "NACO"),
            ("mzt", "MAZATLAN"),
            ("elp", "EL PASO"),
            ("cdmx", "CDMX"),
        ],
        help="Port of input",
    )
    partner_id = fields.Many2one("res.partner", string="Broker", help="Broker of this landed cost")

    def _get_lines_from_invoice(self):
        company_currency = self.env.company.currency_id
        lines = []
        for invoice in self.invoice_ids:
            for line in invoice.invoice_line_ids.filtered(lambda dat: dat.product_id.landed_cost_ok):
                cost = line.price_unit
                if invoice.currency_id != company_currency:
                    cost = invoice.currency_id.with_context(date=invoice.date).compute(
                        line.price_unit, company_currency
                    )
                lines.append(
                    (
                        0,
                        False,
                        {
                            "name": line.product_id.name,
                            "account_id": line.account_id.id,
                            "product_id": line.product_id.id,
                            "price_unit": cost,
                            "split_method": "by_current_cost_price",
                            "segmentation_cost": "landed_cost",
                        },
                    )
                )
        return lines

    @api.onchange("guide_ids", "invoice_ids")
    def _onchange_guide_invoice(self):
        """Inherited from stock.landed.costs in oder to add the logic necessary
        to update the list with the elements extracted when guides are
        added/removed"""
        company_currency = self.env.user.company_id.currency_id
        line_invoice = self._get_lines_from_invoice()
        for landed_cost in self:
            lines = []
            landed_cost.update({"cost_lines": [(5, 0, 0)]})
            for guide in landed_cost.guide_ids:
                for line in guide.line_ids:
                    product = line.product_id
                    account = product.categ_id.property_account_expense_categ_id
                    diff_currency = guide.currency_id != company_currency
                    cost = line.cost
                    if diff_currency:
                        cost = guide.currency_id.with_context(date=guide.date).compute(line.cost, company_currency)
                    lines.append(
                        (
                            0,
                            False,
                            {
                                "name": product.name,
                                "account_id": account,
                                "product_id": product.id,
                                "price_unit": cost,
                                "split_method": "by_current_cost_price",
                                "segmentation_cost": "landed_cost",
                            },
                        )
                    )
            landed_cost.update({"cost_lines": lines + line_invoice})


class StockLandedCostLines(models.Model):
    _inherit = "stock.landed.cost.lines"

    split_method = fields.Selection(default="by_current_cost_price")

    @api.onchange("product_id")
    def onchange_product_id(self):
        # We first load products calling super() method.
        res = super().onchange_product_id()
        self.split_method = "by_current_cost_price"
        return res


class StockValuationAdjustmentLines(models.Model):
    _inherit = "stock.valuation.adjustment.lines"

    picking_id = fields.Many2one("stock.picking", string="Pickings", copy=False)
