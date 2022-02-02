from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    importance = fields.Selection([("aa", "AA"), ("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    note = fields.Text()
    reorder_point = fields.Char()

    def _prepare_procurement_values(self, date=False, group=False):
        """If we're comming from an special SO, use the specified vendor when creating the PO"""
        values = super()._prepare_procurement_values(date=date, group=group)
        values["supplierinfo_name"] = self.env.context.get("supplierinfo_name")
        return values
