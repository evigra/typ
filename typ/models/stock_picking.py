from odoo import _, api, fields, models
from odoo.exceptions import UserError


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
    is_warranty = fields.Boolean(help="True if destination is warranty location")
    responsible_for_warranty = fields.Many2one("res.users")
    arrival_date_broker = fields.Date(states={"done": [("readonly", True)]}, help="Arrival date at the customs broker")
    input_cb = fields.Char(help="Custom Broker code")
    guide_number = fields.Char(help="Guide number")

    @api.onchange("location_dest_id")
    def _onchange_location_dest_id(self):
        self.is_warranty = self.location_dest_id.warranty_location

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
        sale = self.mapped("sale_id")
        if self._context.get("bypass_check_sale") or not sale:
            return False
        if all(picking.state == "cancel" for picking in sale.picking_ids):
            sale.sudo().with_context(bypass_check_sale=True).action_cancel()
            msg = _("Sale order cancelled by %s") % self.env.user.name
            sale.sudo().message_post(body=msg)
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
        sale = self.mapped("sale_id")
        purchases = sale.picking_ids.purchase_id.filtered(lambda order: order.state == "purchase")
        cancel_picking = self._context.get("cancel_picking")
        if (
            not cancel_picking
            and purchases
            and (self.location_dest_id.filtered(lambda pick: pick.usage != "customer") or len(self) > 1)
            and self.filtered(lambda pick: pick.picking_type_id.code != "incoming")
        ):
            raise UserError(_("This order %s cannot be cancelled.") % sale.name)

        pick_done = sale.picking_ids.filtered(lambda pick: pick.state == "done")
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
            "typ.group_cancel_picking_with_move_not_in_transit_loc"
        )
        if group_cancel_pick_move_transit or (not pick_done and sale):
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
        internal_pickings = self.filtered(lambda pick: pick.picking_type_id.code == "internal")
        unallowed_locations = ("customer", "supplier")
        for move in internal_pickings.move_lines:
            if move.location_id.usage in unallowed_locations or move.location_dest_id.usage in unallowed_locations:
                raise UserError(_("Internal movements don't allow locations in supplier or customer"))

        for picking in self:
            if picking.is_warranty and not picking.requirements_for_warranty:
                raise UserError(
                    _(
                        "To transfer this picking to guarantees in process, "
                        "approval of the purchasing department is necessary, "
                        "please contact them."
                    )
                )
        return super().button_validate()
