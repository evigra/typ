# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp import exceptions


class StockMove(models.Model):

    _inherit = "stock.move"

    @api.multi
    def propagate_picking_transfer(self):
        """If stock_move is done verify if it have to propagate transfer to
        move_dest_id.
        """
        if self.state == 'assigned' and\
                self.move_orig_ids.filtered(lambda dat: dat.state == 'done')\
                and self.rule_id.propagate_transfer:
            picking = self.picking_id
            ctx = {
                'active_id': picking.id,
                'active_ids': [picking.id],
                'active_model': 'stock.picking',
            }
            wizard_transfer_id = self.env['stock.transfer_details'].\
                with_context(ctx).create({'picking_id': picking.id})
            wizard_transfer_id.do_detailed_transfer()

    @api.multi
    def validate_picking_negative(self):
        """Validation warehouses to prevent negative numbers. Limiting the
        warehouses not to allow movements generate if no stock.
        """
        if self.state == 'done':
            for move in self.quant_ids:
                if not move.location_id == self.location_dest_id or \
                        move.qty < 0:
                    raise exceptions.Warning(
                        _('Warning!'),
                        _('Negative Quant creation error. Contact personnel '
                          'Vauxoo immediately')
                    )

    @api.multi
    def verify_user_scrap(self):
        """Allows only users group manager/warehouse, confirm and validate
        movements locations losses or scraped
        """
        if self.state == 'assigned':
            if self.location_id.usage == 'internal' and \
                    self.location_dest_id.usage == 'inventory':
                manager = self.env.user.has_group('stock.group_stock_manager')
                if not manager:
                    raise exceptions.Warning(
                        _('Warning!'),
                        _('Permission denied only manager/warehouse group.'
                          ' Contact personnel Vauxoo immediately')
                    )

    @api.model
    def check_tracking_product(self, product, lot_id, location, location_dest):
        """Overwrite method check_tracking_product super
        """
        check = False
        if product.track_all and not location_dest.usage == 'inventory':
            check = True
        elif product.track_incoming and location.usage in (
            'supplier', 'transit', 'inventory') and \
                location_dest.usage == 'internal':
            check = True
        elif product.track_outgoing and location_dest.usage in (
                'customer', 'transit') and location.usage == 'internal':
            check = True
        if check and not lot_id:
            raise exceptions.Warning(
                _('Warning!'),
                _('You must assign a serial number for the product [%s] %s') %
                (product.default_code, product.name))
        return super(StockMove, self).check_tracking_product(
            product, lot_id, location, location_dest)


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.multi
    def name_get(self):

        name = super(StockPicking, self).name_get()
        result = []
        for inv in self:
            result.append(
                (inv.id, "%s %s" % (inv.name or '', inv.origin or ''))
            )
        return result if result else name

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        recs = self.browse()
        if name:
            recs_origin = self.search(
                [('origin', operator, name)] + args,
                limit=limit
            )
            recs_name = self.search(
                [('name', operator, name)] + args,
                limit=limit
            )
            recs = recs_origin | recs_name
        return recs.name_get() or super(StockPicking, self).name_search(
            name, args=args, operator=operator, limit=limit)

    @api.multi
    def validate_move_internal(self):
        """Validates internal movements so that when a movement is generated
        do not allow to customers or suppliers
        """
        if self.picking_type_id.code == 'internal' and self.state == 'done':
            for move in self.move_lines:
                if move.location_id.usage != 'internal' or \
                        move.location_dest_id.usage not in (
                            'internal', 'inventory'):
                    raise exceptions.Warning(
                        _('Warning!'),
                        _('Both locations must be internal type or location '
                          'source type internal and location destination type '
                          'inventory')
                        )

    @api.multi
    def validate_return_customer(self):
        """Restricts the quantity of products by return of a sale does not
        exceed more than invoiced
        """
        if self.picking_type_id.code == 'incoming' and \
                self.state == 'confirmed':
            uom = self.env['product.uom']
            for move in self.move_lines:
                if move.location_id.usage == 'customer':
                    total_move_qty = uom._compute_qty(
                        move.product_uom.id,
                        move.product_uom_qty,
                        move.product_id.uom_id.id,
                    )
                    total_origin_move_qty = sum(move.origin_returned_move_id.
                                                quant_ids.mapped('qty'))

                    if total_move_qty > total_origin_move_qty:
                        raise exceptions.Warning(
                            _('Warning!'),
                            _('The return of the product %s, exceeds the '
                              'amount invoiced') % (move.product_id.name))


class StockWarehouse(models.Model):

    _inherit = "stock.warehouse"

    active = fields.Boolean(default=True)

    @api.multi
    @api.constrains('active')
    def _check_active(self):
        location_ids = self.filtered(lambda x: not x.active).mapped(
            'view_location_id')._get_sublocations()
        if self.env["stock.quant"].search([("location_id", "in",
                                            location_ids)], limit=1):
            msg = _('You can not inactivate a warehouse with products'
                    ' on it, please adjust your inventories first and'
                    ' then come back and inactivate it.')
            raise exceptions.ValidationError(msg)
