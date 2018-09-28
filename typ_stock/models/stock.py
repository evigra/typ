# coding: utf-8

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class StockPicking(models.Model):

    _inherit = "stock.picking"

    picking_shipment_date = fields.Date(
        default=fields.Date.context_today, index=True,
        states={'done': [('readonly', True)]},
        help="Shipment date of the picking"
    )
    invoiced = fields.Boolean(
        'Invoiced complete', copy=False,
        help="This must be checked only when the supplier have invoiced "
        "the whole order and there isn't a backorder. This activate a "
        "green highlight on tree view "
    )
    number_landing = fields.Char(copy=False)

    def action_confirm_trafic(self):
        """This fill the invoiced field automatically"""
        self.ensure_one()
        self.invoiced = not self.invoiced
        data = _("<ul><li>shipment confirmed --> <b>ok</b></li></ul>")
        if not self.invoiced:
            data = _(
                "<ul><li>shipment confirmed --> <b>Canceled</b></li></ul>"
            )
        self.message_post(body=data)

    @api.multi
    def action_cancel(self):
        """Validate that pickings cannot be cancelled with moves in transit
        """
        if self.env.user.has_group(
                'typ_stock.group_cancel_picking_with_move_not_in_transit_loc'):
            return super().action_cancel()
        moves_with_orig_transit_loc = self.move_lines.filtered(
            lambda mv: mv.move_orig_ids.id and
            mv.location_id.usage == 'transit')
        if moves_with_orig_transit_loc:
            raise UserError(_('This picking cannot be cancelled.'))
        return super().action_cancel()

    def _get_overprocessed_stock_moves(self):
        """Validate that pickings cannot be processed more than what was
        initially planned
        """
        self.ensure_one()
        res = super()._get_overprocessed_stock_moves()
        if res:
            raise UserError(
                _('This picking cannot be confirmed because. You '
                  'have processed more than what was initially planned'))
        return res

    @api.multi
    def button_validate(self):
        self.ensure_one()
        """Validates internal movements so that when a movement is generated
        do not allow to customers or suppliers
        """
        if self.picking_type_id.code != 'internal':
            return super().button_validate()
        for move in self.move_lines:
            if (move.location_id.usage in ('customer', 'supplier') or
                    move.location_dest_id.usage in ('customer', 'supplier')):
                raise UserError(
                    _("Internal movements don't allow locations in "
                      "supplier or customer"))
        return super().button_validate()


class StockMove(models.Model):

    _inherit = "stock.move"

    shipment_date = fields.Date(
        'Product shipment date',
        default=fields.Date.context_today, index=True,
        states={'done': [('readonly', True)]},
        help="Scheduled date for the shipment of this move"
    )
    product_supplier_ref = fields.Char(string='Supplier Code')


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        for move in self.product_return_moves:
            product_qty = self.picking_id.returned_ids.mapped(
                'move_lines').filtered(
                    lambda dat: dat.product_id.id == move.product_id.id and
                    dat.state != 'cancel'
                ).mapped('product_qty')
            quantity = move.move_id.product_qty - sum(product_qty)
            quantity = float_round(
                quantity, precision_rounding=move.move_id.product_uom.rounding)
            if move.quantity > quantity:
                raise UserError(_(
                    '[Product: %s, To return: %s]'
                    ' You can not return more quantity than delivered')
                    % (move.product_id.name, quantity))
        return super(ReturnPicking, self)._create_returns()


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    importance = fields.Selection([
        ('aa', 'AA'), ('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')
    ])
    note = fields.Text()
    reorder_point = fields.Char()

