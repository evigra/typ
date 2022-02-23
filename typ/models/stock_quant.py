from odoo import api, models
from odoo.exceptions import RedirectWarning


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def _update_reserved_quantity(
        self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False
    ):
        """Ensure action to fix reserved quantity is run only over involved quants

        Odoo provides an action to fix quants whose reserved quantity is inconsistent with stock moves [1].
        However, that action runs over all quants, which it's inviable for databases with literally
        millions of quants.

        [1] https://github.com/odoo/odoo/pull/79180
        """
        try:
            return super()._update_reserved_quantity(product_id, location_id, quantity, lot_id, package_id, owner_id)
        except RedirectWarning as warning:
            related_quants = self._get_quants_from_context(
                product_id=product_id,
                location_id=location_id,
                quantity=quantity,
                lot_id=lot_id,
                package_id=package_id,
                owner_id=owner_id,
                strict=strict,
            )
            additional_context = dict(
                **warning.args[3] or {},
                search_only_quant_ids=related_quants.ids,
            )
            raise RedirectWarning(*warning.args[:3], additional_context=additional_context) from None

    def _get_quants_from_context(
        self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False
    ):
        """Get related quants depending on the active record

        The following cases are considered:
        - If it's a picking, quants matching all move lines are returned
        - If it's a sale order, quants matching all lines of all deliveries are returned
        """
        # Candidate quants in the current operation
        quants = self._gather(
            product_id=product_id,
            location_id=location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )

        # Related stock move lines from active record
        move_lines = self.env["stock.move.line"]
        active_model = self.env.context.get("active_model", self._name)
        active_id = self.env.context.get("params", {}).get("id") or self.env.context.get("active_id")
        active_record = self.env[active_model].browse(active_id)
        if active_model == "sale.order":
            move_lines |= active_record.picking_ids.move_line_ids
        elif active_model == "stock.picking":
            move_lines |= active_record.move_line_ids

        # Gather quants from all stock move lines
        for line in move_lines:
            quants |= self._gather(
                product_id=line.product_id,
                location_id=line.location_id,
                lot_id=line.lot_id,
                package_id=line.package_id,
                owner_id=line.owner_id,
                strict=strict,
            )

        return quants

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        search_only_quant_ids = self.env.context.get("search_only_quant_ids")
        if not args and search_only_quant_ids:
            args = [("id", "in", search_only_quant_ids)]
        return super().search(args, offset, limit, order, count)
