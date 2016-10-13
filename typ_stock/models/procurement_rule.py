# -*- coding: utf-8 -*-

from openerp import fields, models, api


class ProcurementRule(models.Model):

    _inherit = "procurement.rule"

    propagate_transfer = fields.Boolean(
        string="Propagate transfer",
        help="When this field is check, the first stock move which is"
        " transferred triggers automatically the transfer to the other"
        " stock move related")


class ProcurementOrder(models.Model):

    _inherit = 'procurement.order'

    @api.model
    def _search_suitable_rule(self, procurement, domain):
        """This method it is overwrite in order to allow propagate pule rule
        from warehouse to another when the user has not access.
        e.g. The user A have access only into warehouse A but when create
        one sale order with route that make purchase order to warehouse B and
        resupply the warehouse A we need to propagate procurement to
        warehouse B with procurement.sudo()"""

        return super(ProcurementOrder, self)._search_suitable_rule(
            procurement.sudo(), domain)
