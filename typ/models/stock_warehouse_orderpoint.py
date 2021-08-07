from odoo import fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    importance = fields.Selection([("aa", "AA"), ("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    note = fields.Text()
    reorder_point = fields.Char()
