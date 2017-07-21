# -*- coding: utf-8 -*-

from openerp import models, fields


class PurchaseOrder(models.Model):

    _inherit = "res.company"

    email_purchase = fields.Char()
