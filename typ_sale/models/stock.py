# coding: utf-8

from openerp import _, api, models
from openerp.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        sale = move.picking_id.sale_id
        if sale and inv_type in ('out_invoice', 'out_refund'):
            res.update({
                'payment_term': sale.payment_term.id,
                'type_payment_term': sale.type_payment_term, })
        if 'payment_term' in res:
            date_due = (self.env['account.invoice'].
                        onchange_payment_term_date_invoice(
                            res['payment_term'], False))
            res.update({'date_due': date_due['value']['date_due']})
        return res

    @api.model
    def check_pedimento(self, picking):
        for move in picking.move_lines:
            for quant in move.quant_ids:
                if quant.landed_id:
                    continue
                origin = quant.history_ids.sorted(key=lambda mv: mv.date)
                if (origin and not
                        origin[0].picking_id.partner_id.country_id.code ==
                        'MX'):
                    raise ValidationError(
                        _('It is necessary register a pedimento in entry '
                          'quant before continue. This is not from a mexican '
                          'supplier.'))
        return True

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        """Inherit method to verify existence of pedimento when is a sale and
        the product supplier is not mexican"""
        group_inv_without_ped = bool(
            self.env.user.groups_id &
            self.env.ref('typ_sale.group_invoiced_without_pedimento'))
        if picking.sale_id and not group_inv_without_ped:
            self.check_pedimento(picking)
        return super(StockPicking, self)._create_invoice_from_picking(
            picking, vals)


class StockMove(models.Model):

    _inherit = 'stock.move'

    @api.model
    def _prepare_procurement_from_move(self, move):
        """Inherit to reassign origin field in procurement order"""
        res = super(StockMove, self)._prepare_procurement_from_move(move)
        order = move.procurement_id._get_sale_line_id().order_id
        if order:
            res.update({'origin': order.name})
        return res
