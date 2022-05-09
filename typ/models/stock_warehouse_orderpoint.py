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

    def _procure_orderpoint_confirm(self, use_new_cursor=False, company_id=None, raise_user_error=True):
        group = self.env["procurement.group"].sudo().create({})
        if use_new_cursor:
            self._cr.commit()  # pylint: disable=invalid-commit
        self_ctx = self.with_context(procurement_group=group)
        res = super(StockWarehouseOrderpoint, self_ctx)._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor, company_id=company_id, raise_user_error=raise_user_error
        )
        return res

    def _prepare_procurement_values(self, date=False, group=False):
        res = super()._prepare_procurement_values(date=date, group=group)
        res["group_id"] = self._context.get("procurement_group")
        return res
