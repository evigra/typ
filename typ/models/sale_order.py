
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    @api.depends("order_line")
    def _compute_has_order_lines(self):
        self.has_order_lines = bool(self.order_line)

    has_order_lines = fields.Boolean(
        compute="_compute_has_order_lines",
        help='Helper field to disable partner edition in Form view')

    @api.multi
    def write(self, vals):

        if not vals.get('partner_id'):
            return super(SaleOrder, self).write(vals)

        so_partner_edited = self.filtered(lambda r: r.partner_id.id != vals['partner_id'] and r.has_order_lines)
        if so_partner_edited:
            raise ValidationError(_(
                "You can't change Partner in Sales Orders with lines. Order IDs: %s.") % so_partner_edited.ids)

        return super(SaleOrder, self).write(vals)
