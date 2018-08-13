# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestPurchaseFromSaleOrder(TransactionCase):

    def setUp(self):
        super(TestPurchaseFromSaleOrder, self).setUp()
        self.route = self.env.ref('stock.route_warehouse0_mto')
        self.route_large = self.env.ref(
            'typ_stock.stock_location_route_test_2')
        self.partner = self.env.ref('base.res_partner_1')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.warehouse_large = self.env.ref('typ_stock.whr_test_02')
        self.product = self.env.ref('product.product_delivery_02')
        self.partner_purchase = self.env.ref('base.res_partner_4')
        self.location = self.env.ref('stock.stock_location_stock')
        self.line_vals = {
            'name': self.product.name, 'product_id': self.product.id,
            'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
            'price_unit': 900, 'route_id': self.route.id,
            'purchase_partner_id': self.partner_purchase.id, }
        self.dict_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, self.line_vals)], }

    def test_00_origin_field_purchase_picking(self):
        """Test that purchase order created when sale order is confirmed  and
        the picking created when purchase is confirmed has the correct origin.
        """
        dict_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [
                (0, 0,
                 {'name': self.product.name, 'product_id': self.product.id,
                  'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
                  'price_unit': 900, 'route_id': self.route.id,
                  'purchase_partner_id': self.partner_purchase.id})], }
        sale_order = self.env['sale.order'].create(dict_vals)
        sale_order.action_confirm()
        purchase_order = self.env['purchase.order'].search(
            [('origin', '=', sale_order.name)])
        self.assertTrue(purchase_order)
        purchase_order.button_confirm()
        origin = purchase_order.picking_ids.mapped('origin')[0]
        self.assertEqual(origin, sale_order.name + ':' + purchase_order.name)

    def test_00_special_sale_order_with_simple_route(self):
        """Test that purchase order created when sale order is confirmed has
        as partner_id the partner that was set as Supplier for purchase in
        the sale_order_line.
        """
        seller_id = (self.product.seller_ids.filtered(
            lambda seller: seller.name == self.partner_purchase)).id
        # If the partner that it has been used as Supplier for purchase is into
        # product sellers, remove it to be ensure that do not use that register
        # to create purchase order
        self.product.write({'seller_ids': [(3, seller_id)]})
        self.assertNotIn(self.partner_purchase,
                         [seller.name for seller in self.product.seller_ids])

        sale_order = self.env['sale.order'].create(self.dict_vals)
        sale_order.action_confirm()
        purchase_order = self.env['purchase.order'].search(
            [('origin', '=', sale_order.name)])
        self.assertEqual(sale_order.order_line.purchase_partner_id,
                         purchase_order.partner_id)

    def test_10_special_sale_order_with_large_route(self):
        """Same test test_00_special_sale_order_with_simple_route but with a
        route in sale order line with another configuration.
        """
        self.line_vals.update({'route_id': self.route_large.id})
        self.dict_vals.update(
            {'order_line': [(0, 0, self.line_vals)],
             'warehouse_id': self.warehouse_large.id, })
        sale_order = self.env['sale.order'].create(self.dict_vals)
        sale_order.action_confirm()
        purchase_order = self.env['purchase.order'].search(
            [('origin', 'like', sale_order.name)])
        self.assertEqual(sale_order.order_line.purchase_partner_id,
                         purchase_order.partner_id)
