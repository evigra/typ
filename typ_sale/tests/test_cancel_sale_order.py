# -*- coding: utf-8 -*-

from openerp.exceptions import ValidationError as UserError
from openerp.tests.common import TransactionCase


class TestCancelSaleOrder(TransactionCase):

    def setUp(self):
        super(TestCancelSaleOrder, self).setUp()
        self.product = self.env.ref('product.product_product_6')
        self.partner = self.env.ref('base.res_partner_1')
        self.warehouse = self.env.ref('typ_stock.whr_test_01')
        self.route = self.env.ref('typ_stock.stock_location_route_test_1')
        self.stock_picking = self.env['stock.picking']
        self.transfer_obj = self.env['stock.transfer_details']

        self.dict_vals_line = {
            'name': self.product.name,
            'product_id': self.product.id,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'price_unit': 2000,
            'route_id': self.route.id,
        }

        self.dict_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.ref('product.list0'),
            'warehouse_id': self.warehouse.id,
            'order_line': [(0, 0, self.dict_vals_line)], }

    def test_10_allow_cancel_order(self):
        sale_order = self.env['sale.order'].create(self.dict_vals)
        sale_order.action_button_confirm()

        self.assertNotIn('done', sale_order.picking_ids.mapped('state'))

        sale_order.action_cancel()
        self.assertTrue(sale_order.state, 'cancel')

    def test_20_not_allow_cancel_order(self):
        sale_order = self.env['sale.order'].create(self.dict_vals)
        sale_order.action_button_confirm()

        first_pick = sale_order.picking_ids.filtered(
            lambda pick: pick.state == 'confirmed')
        self.env['stock.quant'].create({
            'location_id': first_pick.location_id.id,
            'product_id': self.product.id,
            'qty': 1.0,
        })
        first_pick.action_assign()

        ctx = {
            "active_id": first_pick.id,
            "active_ids": [first_pick.id],
            "active_model": "stock.picking",
        }
        self.env['stock.transfer_details'].with_context(ctx).create(
            {'picking_id': first_pick.id, }).do_detailed_transfer()

        self.assertIn('done', sale_order.picking_ids.mapped('state'))

        msg = ('This order can not be canceled because some of their '
               'pickings already have been transfered.')
        with self.assertRaisesRegexp(UserError, msg):
            sale_order.action_cancel()
