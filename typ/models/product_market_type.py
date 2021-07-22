import logging
from odoo import fields, models


class ProductMarketType(models.Model):
    _name = "product.market.type"
    _description = "TODO: Once talk with the team describe it for v14.0"

    name = fields.Char(required=True)
