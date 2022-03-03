from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    importance = fields.Selection([("aa", "AA"), ("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    note = fields.Text()
    reorder_point = fields.Char()

    def _get_product_context(self):
        """Don't consider lead times when scheduler computes forecasted quantities"""
        context = super()._get_product_context()
        context.pop("to_date", None)
        return context
