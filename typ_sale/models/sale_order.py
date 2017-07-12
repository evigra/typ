# coding: utf-8

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    procurement_group_id = fields.Many2one('procurement.group', select=True)
    picking_ids = fields.One2many(compute='_get_picking_ids') # noqa pylint: disable=method-compute
    pos = fields.Boolean('Is PoS?')

    type_payment_term = fields.Selection(
        [('credit', 'Credit'), ('cash', 'Cash'),
         ('postdated_check', 'Postdated check')], default='credit')

    @api.onchange('warehouse_id', 'partner_id')
    def get_salesman_from_warehouse_config(self):
        """Obtain Salesman depending on configuration warehouse in partner
        related
        """
        res = self.onchange_warehouse_id(self.warehouse_id.id)
        for key in res.get('value').keys():
            if not hasattr(self, key):
                del res['value'][key]
        # Reasign values obtain in original onchange
        self.update(res['value'])
        warehouse_config = self.partner_id.res_warehouse_ids.filtered(
            lambda wh_conf: wh_conf.warehouse_id == self.warehouse_id)
        if warehouse_config:
            self.user_id = warehouse_config.user_id.id

    @api.model
    def _prepare_order_line_procurement(self, order, line, group_id=False):
        """Inherit to reassign origin field in procurement order"""
        res = super(SaleOrder, self)._prepare_order_line_procurement(
            order, line, group_id)
        res.update({'origin': order.name})
        return res

    @api.onchange('type_payment_term', 'partner_id')
    def get_payment_term(self):
        """Get payment term depends on type payment term.
        """
        if self.partner_id:
            if self.type_payment_term in ('cash', 'postdated_check'):
                for payment_term in \
                        self.env['account.payment.term'].search([]):
                    if payment_term.payment_type == 'cash':
                        self.payment_term = payment_term.id
                        break
            else:
                self.payment_term = self.partner_id.property_payment_term.id
            if self.type_payment_term == 'credit' and \
                    (not self.payment_term or
                        self.payment_term.payment_type == 'cash'):
                self.type_payment_term = 'cash'
            elif self.type_payment_term in ('cash', 'postdated_check') and \
                    self.payment_term.payment_type == 'credit':
                self.type_payment_term = 'credit'

    @api.onchange('order_line')
    def check_margin(self):
        """Verify margin minimum in sale order by change in field.
        """
        for line in self.order_line:
            warning = line.check_margin_qty()
            if warning:
                warning['title'] = _('Sale of product below margin')
                return {
                    'warning': warning,
                }

    @api.multi
    def action_cancel(self):
        picking_done = self.picking_ids.filtered(
            lambda pick: pick.state == 'done')
        if picking_done:
            raise ValidationError(_('This order can not be canceled because '
                                    'some of their pickings already have been '
                                    'transfered.'))
        return super(SaleOrder, self).action_cancel()

# -------------------------------------------------------------------------
        # POS methods
# -------------------------------------------------------------------------

    @api.multi
    def _get_picking_ids(self):  # pylint: disable=missing-return
        picking_obj = self.env['stock.picking']
        res = super(SaleOrder, self)._get_picking_ids(
            name='picking_ids', args=None)
        for order in self:
            picking_ids = res.get(order.id)
            if order.pos:
                picking_ids = picking_obj.search([('order_id', '=', order.id)])
            order.picking_ids = picking_ids

    @api.multi
    def action_button_confirm(self):
        """When sale order is checked pos field we return the view of the
        picking in order to save extra click to go to picking view"""
        res = super(SaleOrder, self).action_button_confirm()
        for order in self.filtered('pos'):
            if order.invoice_exists:
                return order.action_view_invoice()
            return order.action_view_delivery()
        return res

    @api.multi
    def action_ship_create(self):
        """When in sale order is checked pos field we make the picking like
        Point of Sale without procurement in order to improve the performance
        when confirm sale order
        """

        picking_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']

        for order in self:

            # If the sale order is not checked the pos fields we return the
            # same behavior
            if not order.pos:
                return super(SaleOrder, order).action_ship_create()

            addr = order.partner_id.address_get(['delivery'])
            picking_type = order.warehouse_id.out_type_id

            picking_id = picking_obj.create({
                'origin': order.name,
                'partner_id': addr.get('delivery'),
                'date_done': order.date_order,
                'picking_type_id': picking_type.id,
                'company_id': order.company_id.id,
                'move_type': 'direct',
                'note': order.note or "",
                'order_id': order.id
            })

            location_id = order.warehouse_id.wh_input_stock_loc_id.id
            destination_id = order.partner_id.property_stock_customer.id

            for line in order.order_line.filtered(
                    lambda dat: not dat.product_id.type == 'service'):

                move_obj.create({
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id.id,
                    'picking_type_id': picking_type.id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.product_uom_qty),
                    'product_uom_qty': abs(line.product_uom_qty),
                    'invoice_state': '2binvoiced',
                    'state': 'draft',
                    'location_id': location_id,
                    'location_dest_id': destination_id,
                    'sale_order_line_id': line.id,
                })
            # we confirm the picking, reserve and transfer if it is allowed
            if not picking_id.create_picking_pos():
                return True
            # Invoice from picking if it is allowed
            picking_id.automatic_invoiced_from_picking()
        return True

    @api.multi
    def check_picking_done(self):
        """Function that validates whether a picking delivered"""
        self.ensure_one()
        picking_valid = not self.env['stock.picking'].search([
            ('id', 'in', self.picking_ids.ids),
            ('state', 'not in', ['cancel', 'done'])], limit=1)
        return picking_valid

    @api.model
    def automatic_sale_pos_done(self):
        """Look for sales orders of type pos in progress status changing to
        done status"""
        sale_ids = self.search([
            ('state', '=', 'progress'), ('pos', '=', True)])
        sale_ids.filtered(
            lambda r: r.check_picking_done()).write({'state': 'done'})
        return True


class StockMove(models.Model):

    _inherit = 'stock.move'

    sale_order_line_id = fields.Many2one('sale.order.line')
    procurement_id = fields.Many2one('procurement.order', select=True)

    @api.model
    def _create_invoice_line_from_vals(self, move, invoice_line_vals):
        """When sale order is checked pos field the picking created is not
        related to procurement and then we need to get invoices information
        from relation between stock.move and sale.order.line"""

        invoice_line_id = super(
            StockMove, self)._create_invoice_line_from_vals(
                move, invoice_line_vals)
        if move.sale_order_line_id.order_id.pos:
            sale_line = move.sale_order_line_id
            sale_line.write({'invoice_lines': [(4, invoice_line_id)]})
            sale_line.order_id.write(
                {'invoice_ids': [(4, invoice_line_vals['invoice_id'])]})
        return invoice_line_id

    @api.model
    def _get_master_data(self, move, company):
        """We need to get invoice partner address and salesman from
        relation between stock.move and sale.order.line and when the is extra
        move there is no relation with the sale.order.line and then we need
        take information from picking.order_id"""

        order_id = move.sale_order_line_id.order_id or move.picking_id.order_id
        if order_id.pos:
            return (
                order_id.partner_invoice_id,
                order_id.user_id.id,
                order_id.pricelist_id.currency_id.id)
        return super(StockMove, self)._get_master_data(move, company)

    @api.model
    def _get_invoice_line_vals(self, move, partner, inv_type):
        """We need to get the price unit and tax of the
        sale order from relation between stock.move and sale.order.line
        """
        res = super(StockMove, self)._get_invoice_line_vals(
            move, partner, inv_type)
        if move.sale_order_line_id.order_id.pos:
            sale_line = move.sale_order_line_id
            res['invoice_line_tax_id'] = [(6, 0, [sale_line.tax_id.ids])]
            res['account_analytic_id'] = sale_line.order_id.project_id.id
            res['discount'] = sale_line.discount
            res['price_unit'] = sale_line.price_unit
        return res

    @api.model
    def _prepare_procurement_from_move(self, move):
        """Inherit to reassign origin field in procurement order"""
        res = super(StockMove, self)._prepare_procurement_from_move(move)
        order = move.procurement_id._get_sale_line_id().order_id
        if order:
            res.update({'origin': order.name})
        return res
