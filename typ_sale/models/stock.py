# coding: utf-8

from openerp import _, api, models, fields
from openerp.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = 'stock.picking'

    order_id = fields.Many2one('sale.order')

    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):
        res = super(StockPicking, self)._get_invoice_vals(
            key, inv_type, journal_id, move)
        sale = move.sale_order_line_id.order_id or move.picking_id.sale_id
        if sale and inv_type in ('out_invoice', 'out_refund'):
            res.update({
                'payment_term': sale.payment_term.id,
                'type_payment_term': sale.type_payment_term,
                'fiscal_position': sale.fiscal_position.id,
                'user_id': sale.user_id.id,
                'section_id': sale.section_id.id,
                'name': sale.client_order_ref or '',
                'comment': sale.note
            })
        if 'payment_term' in res:
            date_due = (self.env['account.invoice'].
                        onchange_payment_term_date_invoice(
                            res['payment_term'], False))
            res.update({'date_due': date_due['value']['date_due']})
        return res

    @api.model
    def check_pedimento(self, picking):
        move_obj = self.env['stock.move']
        company_country_id = self.env.user.company_id.country_id
        for move in picking.move_lines:
            for quant in move.quant_ids:
                if quant.landed_id:
                    continue
                self._cr.execute(
                    """SELECT MIN(move_id) AS move_id
                    FROM stock_quant_move_rel
                    WHERE quant_id=%s""", (quant.id,))
                dat = self._cr.dictfetchall()
                move_id = dat[0] if dat else {}
                origin = move_obj.browse(move_id.get('move_id'))
                country_id = origin.picking_id.partner_id.country_id
                if (country_id and country_id != company_country_id or
                    not country_id and
                    origin.product_id.seller_ids.filtered(
                        lambda sel:
                        sel.name.country_id != company_country_id)):
                    product = origin[0].product_id
                    picking = origin[0].picking_id
                    raise ValidationError(
                        _('It is necessary register a pedimento in entry '
                          'quant of the product %s in picking %s before '
                          'continue. The supplier %s is not a mexican '
                          'supplier.' % (product.name, picking.name,
                                         picking.partner_id.name)))
        return True

    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        """Inherit method to verify existence of pedimento when is a sale and
        the product supplier is not mexican"""
        group_inv_without_ped = bool(
            self.env.user.groups_id &
            self.env.ref('typ_sale.group_invoiced_without_pedimento'))
        if all([vals.get('type') == 'out_invoice',
                not group_inv_without_ped]):
            for pick in self.browse(self._context.get('active_ids')):
                self.check_pedimento(pick)
        return super(StockPicking, self)._create_invoice_from_picking(
            picking, vals)
