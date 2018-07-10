# -*- coding: utf-8 -*-

from openerp import models


class ProcurementRule(models.Model):

    _inherit = "procurement.rule"

    def _make_po_get_domain(self, values, partner):
        """ Resolve the purchase from procurement, which may result in a new
        PO creation and a new PO line creation if it cames from a sale order,
        otherwise, can result in a modification to an existing PO and
        their lines PO.

        @return: dictionary giving for each procurement its related resolving
        PO line.
        """
        if not (self.action == 'buy' and
                self.route_id.sale_selectable):
            return super(ProcurementRule, self)._make_po_get_domain(
                values, partner)
        return (('group_id', '=', ''),)
