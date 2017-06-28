# -*- coding: utf-8 -*-

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp


class StockManualTransfer(models.Model):

    _name = 'stock.manual_transfer'
    _inherit = ['mail.thread']

    name = fields.Char(copy=False, readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse',
                                   required=True, default=lambda self: self.
                                   env.user.default_section_id.
                                   default_warehouse.id)
    date_planned = fields.Date('Planned Date',
                               default=fields.Date.context_today,
                               required=True)
    route_id = fields.Many2one('stock.location.route', 'Preferred Routes',
                               domain=[
                                   ('manual_transfer_selectable', '=', True)],
                               required=True)
    transfer_line = fields.One2many('stock.manual_transfer_line',
                                    'transfer_id',
                                    string='Transfer Lines', copy=True)
    state = fields.Selection([('draft', 'Draft'), ('valid', 'Valid')],
                             default='draft', track_visibility='onchange')
    procurement_group_id = fields.Many2one('procurement.group',
                                           'Procurement Group', copy=False)
    picking_ids = fields.One2many('stock.picking',
                                  compute='_compute_picking_ids')

    @api.multi
    def make_transfer(self):
        if not self.procurement_group_id:
            self.procurement_group_id = self.env["procurement.group"].create({
                'name': self.name,
                'partner_id': self.warehouse_id.company_id.id
            })

        procurement_obj = self.env['procurement.order']
        for line in self.transfer_line:
            procurement_obj.create({
                'name': line.product_id.name,
                'origin': self.name,
                'date_planned': self.date_planned,
                'product_id': line.product_id.id,
                'product_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'warehouse_id': self.warehouse_id.id,
                'location_id': self.warehouse_id.lot_stock_id.id,
                'company_id': self.warehouse_id.company_id.id,
                'group_id': self.procurement_group_id.id,
                'route_ids': [(6, 0, [self.route_id.id])],
            })
        self.state = 'valid'

    @api.multi
    @api.depends('procurement_group_id')
    def _compute_picking_ids(self):
        for record in self.filtered('procurement_group_id'):
            record.picking_ids = record.env['stock.picking'].search(
                [('group_id', '=', record.procurement_group_id.id)])

    @api.multi
    def unlink(self):
        for record in self.filtered(lambda r: r.state == 'valid'):
            raise ValidationError(_(
                'You can not delete a valid transaction! (%s)') % record.name)
        return super(StockManualTransfer, self).unlink()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('manual.transfers')
        return super(StockManualTransfer, self).create(vals)

    @api.multi
    def action_view_pickings(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        if len(self.picking_ids) > 1:
            action['domain'] = [('id', 'in', self.picking_ids.ids)]
        elif self.picking_ids:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = self.picking_ids.id
        return action


class StockManualTransferLine(models.Model):

    _name = 'stock.manual_transfer_line'

    transfer_id = fields.Many2one('stock.manual_transfer',
                                  'Transfer Reference')
    product_id = fields.Many2one('product.product', 'Product',
                                 domain=[('type', '=', 'product')],
                                 ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure',
                                  required=True)

    @api.multi
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom = self.product_id.uom_id
        return {'domain': {'product_uom': [
            ('category_id', '=', self.product_id.uom_id.category_id.id)]}}
