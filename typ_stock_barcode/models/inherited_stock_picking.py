from odoo import models, api, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    progress_char = fields.Char(
        "Progress", compute="_compute_progress", store=True, help="Display progress of current Picking in x/x notation"
    )

    progress = fields.Float(
        "Progress Rate",
        compute="_compute_progress",
        store=True,
        group_operator="avg",
        help="Display progress of current Picking",
    )

    @api.depends("move_line_ids.qty_done")
    def _compute_progress(self):
        for pick in self:
            total = len(pick.move_line_ids)
            scanned_lines = len(pick.move_line_ids.filtered(lambda x: x.qty_done > 0))
            if scanned_lines:
                if scanned_lines >= total:
                    pick.progress = 100
                else:
                    pick.progress = round(100.0 * scanned_lines / total, 2)
            else:
                pick.progress = 0.0
            pick.progress_char = "%s/%s" % (scanned_lines, total)

    def get_po_to_split_from_barcode_no_tracking(self, barcode):
        """Returns the no tracking visible product wizard's action for the
        move line matching the barcode. This method is intended to be called by
        the `picking_no_tracking_barcode_handler` javascript widget when the
        user scans the barcode of a tracked product.
        """
        candidates = self.env["stock.move.line"].search(
            [
                ("picking_id", "in", self.ids),
                ("product_barcode", "=", barcode),
            ]
        )
        product_id = candidates.mapped("product_id")

        action_ctx = dict(
            self.env.context,
            default_picking_id=self.id,
            default_product_id=product_id.id,
            candidates=candidates.ids,
            default_barcode=barcode,
        )
        view_id = self.env.ref("typ_stock_barcode.view_barcode_notracking_form").id
        return {
            "name": _("%s set.") % product_id.display_name,
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "stock.barcode.notracking",
            "views": [(view_id, "form")],
            "view_id": view_id,
            "target": "new",
            "context": action_ctx,
        }

    def on_barcode_scanned(self, barcode):
        suitable_line = self.move_line_ids.filtered(lambda l: l.product_barcode == barcode)
        if not suitable_line:
            raise UserError(_("This product is not in the order: %s") % (barcode))
        return super().on_barcode_scanned(barcode)
