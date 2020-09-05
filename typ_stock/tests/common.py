
from openerp.tests import common


class TestTypStock(common.TransactionCase):

    def setUp(self):
        super(TestTypStock, self).setUp()

        self.product = self.env.ref('product.product_product_6')
        self.partner = self.env.ref('base.res_partner_9')
        self.warehouse = self.env.ref('typ_stock.whr_test_01')
        self.warehouse_2 = self.env.ref('typ_stock.whr_test_02')
        self.route = self.env.ref('typ_stock.stock_location_route_test_1')
        self.route_2 = self.env.ref('typ_stock.stock_location_route_test_2')
        self.route_3 = self.env.ref('typ_stock.stock_location_route_test_3')
        self.stock_picking = self.env['stock.picking']
        self.picking_type = self.env.ref('stock.picking_type_in')
        self.picking_type_out = self.env.ref('stock.picking_type_out')
        self.transfer_obj = self.env['stock.transfer_details']
        self.lot = self.env['stock.production.lot']
        self.group_cancel_picking = self.env.ref(
            'typ_stock.group_cancel_picking_with_move_not_in_transit_loc')
        self.env.user.write({'groups_id': [(4, self.group_cancel_picking.id)]})
        self.country_mx = self.env.ref('base.mx')
        self.partner.write({'country_id': self.country_mx.id})

        self.purchase_order = self.env.ref('purchase.purchase_order_5')

        self.dict_vals_line = {
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom_qty': 3,
            'product_uom': self.product.uom_id.id,
            'price_unit': 900,
            'route_id': self.route.id,
        }

        self.dict_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'picking_policy': 'direct',
            'pricelist_id': self.ref('product.list0'),
            'warehouse_id': self.warehouse.id,
            'order_line': [
                (0, 0, self.dict_vals_line)], }

        self.sale_order = self.env['sale.order'].create(self.dict_vals)
        self.sale_order.action_button_confirm()

        self.first_pick = [pick for pick in self.sale_order.picking_ids if
                           pick.state == 'confirmed'][0]
        self.quant = self.env['stock.quant'].create({
            'location_id': self.first_pick.location_id.id,
            'product_id': self.product.id,
            'qty': 3.0,
        })
        self.first_pick.action_assign()

        transfer_obj = self.env['stock.transfer_details']
        ctx = {
            "active_id": self.first_pick.id,
            "active_ids": [self.first_pick.id],
            "active_model": "stock.picking",
        }
        self.wizard_transfer_id = transfer_obj.with_context(ctx).create({
            'picking_id': self.first_pick.id, })

    def create_picking_default(self, extra_values=None, line=None,  user=None):
        """Create picking with parameters basic"""

        user = user or self.env.user
        extra_values = extra_values or {}
        line = line or {}

        # default
        values = dict(
            partner_id=self.partner.id,
            origin='1234',
            picking_type_id=self.picking_type.id,
        )
        values.update(extra_values)

        # picking line values
        line_values = self.picking_line_defaults()
        line_values.update(line)

        values.update(move_lines=[(0, 0, line_values)])
        return self.stock_picking.sudo(user).create(values)

    def picking_line_defaults(self, extra_values=None):
        """Return a dictionary to be use to add a new move line to
        a picking. This are the default values used to create a picking
        line new values can be given.
        :return dictionary
        """
        extra_values = extra_values or {}

        location_src = self.picking_type.default_location_src_id.id
        location_dest = self.picking_type.default_location_dest_id.id

        values = dict(
            product_id=self.product.id,
            name=self.product.name,
            product_uom_qty=5,
            product_uom=self.product.uom_id.id,
            price_unit=self.product.list_price,
            location_id=location_src,
            location_dest_id=location_dest,
        )
        values.update(extra_values)
        return values

    def update_product_qty(self):
        self.lot_1 = self.lot.create({
            'name': 'lot_1',
            'product_id': self.product_test.id})
        self.lot_2 = self.lot.create({
            'name': 'lot_2',
            'product_id': self.product_test.id})
        self.env['stock.change.product.qty'].create({
            'location_id': self.warehouse.lot_stock_id.id,
            'product_id': self.product_test.id,
            'lot_id': self.lot_1.id,
            'new_quantity': 1
        }).change_product_qty()
        self.env['stock.change.product.qty'].create({
            'location_id': self.warehouse.lot_stock_id.id,
            'product_id': self.product_test.id,
            'lot_id': self.lot_2.id,
            'new_quantity': 1
        }).change_product_qty()
