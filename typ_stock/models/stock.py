from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round
from odoo.tools.safe_eval import safe_eval


class StockLocations(models.Model):

    _inherit = "stock.location"

    warranty_location = fields.Boolean(
        "Is a Warranty Location?",
        help="Check this box to " "allow the use of this location for " "warranties in process.",
    )


class StockPicking(models.Model):

    _inherit = "stock.picking"

    picking_shipment_date = fields.Date(
        default=fields.Date.context_today,
        index=True,
        states={"done": [("readonly", True)]},
        help="Shipment date of the picking",
    )
    invoiced = fields.Boolean(
        "Invoiced complete",
        copy=False,
        help="This must be checked only when the supplier have invoiced "
        "the whole order and there isn't a backorder. This activate a "
        "green highlight on tree view ",
    )
    number_landing = fields.Char(copy=False)
    requirements_for_warranty = fields.Boolean(
        "Meets requirements for warranty?",
        help="Check this box when the requirements for guarantee are fulfilled"
        " in order to transfer it to guarantees in process.",
        copy=False,
    )
    is_warranty = fields.Boolean(help="True if destiny is warranty location")
    responsible_for_warranty = fields.Many2one("res.users")
    arrival_date_broker = fields.Date(states={"done": [("readonly", True)]}, help="Arrival date at the customs broker")
    input_cb = fields.Char(help="Custom Broker code")
    guide_number = fields.Char(help="Guide number")

    @api.onchange("location_dest_id")
    def onchange_dest_warranty(self):
        self.is_warranty = self.location_dest_id.warranty_location

    def _check_allow_write(self, vals):
        """Validate which fields the user can write when warehouse of the
        picking is not the same of the sale team of the user"""

        if vals is None:
            vals = {}

        allow_fields = safe_eval(self.sudo().env["ir.config_parameter"].get_param("stock_picking_allow_fields"))

        if set(vals.keys()).difference(allow_fields):
            raise UserError(_("You are not allowed to do this change"))

    def write(self, vals):
        # check if the user can modify the fields depending of the sales team
        for picking in self.filtered(
            lambda dat: dat.warehouse_id not in (dat.env.user.sale_team_ids.mapped("default_warehouse"))
            and dat.env.user.id != SUPERUSER_ID
        ):
            picking._check_allow_write(vals)
        return super().write(vals)

    def action_confirm_trafic(self):
        """This fill the invoiced field automatically"""
        self.ensure_one()
        self.invoiced = not self.invoiced
        data = _("<ul><li>shipment confirmed --> <b>ok</b></li></ul>")
        if not self.invoiced:
            data = _("<ul><li>shipment confirmed --> <b>Canceled</b></li></ul>")
        self.message_post(body=data)

    def action_cancel_sale(self):
        """Cancel sale order related to picking if all picking are canceled"""
        sale_id = self.mapped("sale_id")
        if self._context.get("bypass_check_sale") or not sale_id:
            return False
        if all(picking.state == "cancel" for picking in sale_id.picking_ids):
            sale_id.sudo().with_context(bypass_check_sale=True).action_cancel()
            msg = _("Sale order cancelled by %s") % self.env.user.name
            sale_id.sudo().message_post(body=msg)
        return True

    def action_cancel(self):
        """Validate that pickings cannot be cancelled with moves in transit."""
        # Search for sale orders with special purchase order, in a confirmed
        # state and that do not have as destination the location of the
        # customer, to avoid the cancellation of the picking
        # For this case: the incoming pickings are ignored, because
        # the pickings retuned by the customer, generated by empty partial
        # deliveries, can be canceled. Also partial entries not received
        move_model = self.env["stock.move"]
        sale_id = self.mapped("sale_id")
        purchase_ids = sale_id.picking_ids.mapped("purchase_id").filtered(lambda order: order.state == "purchase")
        cancel_picking = self._context.get("cancel_picking", False)
        if (
            not cancel_picking
            and purchase_ids
            and (self.mapped("location_dest_id").filtered(lambda pick: pick.usage != "customer") or len(self) > 1)
            and self.filtered(lambda pick: pick.picking_type_id.code != "incoming")
        ):
            raise UserError(_("This order %s cannot be cancelled.") % sale_id.name)

        pick_done = sale_id.picking_ids.filtered(lambda pick: pick.state == "done")
        moves_with_transit_loc = move_model.search(
            [("picking_id", "in", self.ids), ("location_id.usage", "=", "transit")]
        )

        # Movement origin to cancel, as long as they are not processed,
        # so they do not remain in the transit location
        move_origns = move_model.search([("move_dest_ids", "in", moves_with_transit_loc.ids), ("state", "!=", "done")])
        move_origns._action_cancel()

        # It allows canceling movements of same supply if all its states have
        # not been transferred, when it is a special order or belong to the
        # group that allows it to cancel pickings in transit
        group_cancel_pick_move_transit = self.env.user.has_group(
            "typ_stock.group_cancel_picking_with_move_not_in_transit_loc"
        )
        if group_cancel_pick_move_transit or (not pick_done and sale_id):
            res = super().action_cancel()
            self.action_cancel_sale()
            return res

        # Verify if there are transfers transferred to transit pending receipt
        moves_with_transit_loc._action_assign()
        reserved_availability_transit = sum(moves_with_transit_loc.mapped("reserved_availability"))
        if reserved_availability_transit != 0.0:
            picks = ",".join(moves_with_transit_loc.mapped("picking_id.name"))
            raise UserError(_("This picking %s cannot be cancelled.") % picks)
        moves = move_model.search([("picking_id", "in", self.ids), ("location_id.usage", "!=", "transit")])
        moves_dest_with_transit = move_model.search(
            [("move_orig_ids", "in", moves.ids), ("location_id.usage", "=", "transit")]
        )
        res = super().action_cancel()
        self.action_cancel_sale()

        # Send messages to movements of transit destination
        message = _("This pickings has been canceled: %s") % (
            ",".join(
                [
                    "<a href=# data-oe-model=stock.picking data-oe-id=" + str(pick.id) + ">" + pick.name + "</a>"
                    for pick in self
                ]
            )
        )
        for pick in moves_dest_with_transit.mapped("picking_id"):
            pick.message_post(body=message)
        return res

    def _get_overprocessed_stock_moves(self):
        """Validate that pickings cannot be processed more than what was
        initially planned
        """
        self.ensure_one()
        res = super()._get_overprocessed_stock_moves()
        if res:
            raise UserError(
                _(
                    "This picking cannot be confirmed because. You "
                    "have processed more than what was initially planned"
                )
            )
        return res

    def button_validate(self):
        """Validates internal movements so that when a movement is generated,
        do not allow to customers or suppliers
        """
        self.ensure_one()

        move_line_ids = self.move_line_ids.filtered(
            lambda dat: dat.product_id.tracking != "none"
            and not dat.move_id.move_orig_ids
            and not dat.serial_id
            and dat.location_id.usage == "internal"
        )
        if move_line_ids:
            raise UserError(
                _("You need to supply a lot/serial number for %s.") % move_line_ids.mapped("product_id.name")
            )

        if self.picking_type_id.code != "internal":
            return super().button_validate()
        for move in self.move_lines:
            if move.location_id.usage in ("customer", "supplier") or move.location_dest_id.usage in (
                "customer",
                "supplier",
            ):
                raise UserError(_("Internal movements don't allow locations in " "supplier or customer"))
        if self.is_warranty and not self.requirements_for_warranty:
            raise UserError(
                _(
                    "To transfer this picking to guarantees in process, "
                    "approval of the purchasing department is necessary, "
                    "please contact them."
                )
            )
        return super().button_validate()

    def _create_backorder(self, backorder_moves=list):
        """Send message a picking transit for new backorder picking."""
        backorders = super()._create_backorder(backorder_moves)
        moves_orig_with_transit = backorders.mapped("move_lines.move_orig_ids").filtered(
            lambda mv: mv.location_dest_id.usage == "transit"
        )
        message = _("Back order has been created in destination: %s") % (
            ",".join(
                [
                    "<a href=# data-oe-model=stock.picking data-oe-id=" + str(pick.id) + ">" + pick.name + "</a>"
                    for pick in backorders
                ]
            )
        )
        for pick in moves_orig_with_transit.mapped("picking_id"):
            pick.message_post(body=message)
        return backorders


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    serial_id = fields.Many2one("stock.production.lot", "Serial")

    @api.onchange("lot_name", "lot_id", "serial_id")
    def onchange_serial_number(self):
        res = super().onchange_serial_number()
        lot_id = self.env["stock.production.lot"].search([("id", "=", self.serial_id.id)], limit=1)

        self.lot_id = lot_id.id
        self.qty_done = 0
        return res

    def write(self, vals):
        res = super().write(vals)

        quant_obj = self.env["stock.quant"]

        for move_line_id in self.mapped("picking_id.move_line_ids").filtered(
            lambda dat: dat.serial_id and dat.qty_done == 0.0
        ):
            if move_line_id.product_uom_qty == 0.0:
                move_line_id.with_context(bypass_reservation_update=True).product_uom_qty = 1
            quant_id = quant_obj.search([("lot_id", "=", move_line_id.lot_id.id)])
            quant_id.write({"reserved_quantity": 0.0})
            quant_obj._update_reserved_quantity(
                move_line_id.product_id, move_line_id.location_id, 0, lot_id=move_line_id.lot_id, strict=True
            )
            quant_obj._update_reserved_quantity(
                move_line_id.product_id, move_line_id.location_id, 1, lot_id=move_line_id.lot_id, strict=True
            )

        return res


class StockMove(models.Model):

    _inherit = "stock.move"

    sale_line_id = fields.Many2one(index=True)

    shipment_date = fields.Date(
        "Product shipment date",
        default=fields.Date.context_today,
        index=True,
        states={"done": [("readonly", True)]},
        help="Scheduled date for the shipment of this move",
    )
    product_supplier_ref = fields.Char(string="Supplier Code")
    product_shipment_date = fields.Date(
        related="picking_id.picking_shipment_date", help="Product picking shipment date"
    )

    def _push_apply(self):
        return super(StockMove, self.sudo())._push_apply()

    def _action_confirm(self, merge=True, merge_into=False):
        group_id = self._context.get("group_id")
        for move in self.filtered(lambda dat: not dat.group_id and group_id):
            move.group_id = group_id
            merge = False
        return super()._action_confirm(merge=merge, merge_into=merge_into)

    def _action_done(self):
        for move in self.filtered(lambda dat: not dat.inventory_id):
            if not move.location_id.should_bypass_reservation() and move.quantity_done > move.reserved_availability:
                raise UserError(_("You can not transfer different reserved"))
        return super()._action_done()


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):
        for move in self.product_return_moves:
            product_qty = (
                self.picking_id.returned_ids.mapped("move_lines")
                .filtered(lambda dat: dat.product_id.id == move.product_id.id and dat.state != "cancel")
                .mapped("product_qty")
            )
            quantity = move.move_id.product_qty - sum(product_qty)
            quantity = float_round(quantity, precision_rounding=move.move_id.product_uom.rounding)
            if move.quantity > quantity:
                raise UserError(
                    _("[Product: %s, To return: %s]" " You can not return more quantity than delivered")
                    % (move.product_id.name, quantity)
                )
        return super()._create_returns()


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    importance = fields.Selection([("aa", "AA"), ("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    note = fields.Text()
    reorder_point = fields.Char()


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    def action_validate(self):
        """Allows only users group manager/warehouse, confirm and validate, the
        movements locations losses or scraped
        """
        self.ensure_one()
        if self.location_id.usage == "internal" and self.scrap_location_id.usage == "inventory":
            manager = self.env.user.has_group("stock.group_stock_manager")
            if not manager:
                raise UserError(
                    _("Permission denied only manager/warehouse group." " Contact personnel Vauxoo immediately")
                )
        return super().action_validate()


class PurchaseOrderLine(models.Model):

    _inherit = "purchase.order.line"

    def _prepare_stock_moves(self, picking):
        res = super()._prepare_stock_moves(picking)
        if res:
            supplier = self.product_id.seller_ids.filtered(
                lambda r: r.name == self.order_id.partner_id and r.product_id == self.product_id
            )
            supplier = supplier and supplier[0] or supplier
            res[0].update(
                {"product_supplier_ref": supplier.product_code, "shipment_date": picking.picking_shipment_date}
            )
        return res
