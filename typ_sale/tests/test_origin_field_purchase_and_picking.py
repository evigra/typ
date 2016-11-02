# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestOriginFieldPurchasePicking(TransactionCase):

    def setUp(self):
        super(TestOriginFieldPurchasePicking, self).setUp()
        self.route = self.env.ref('stock_dropshipping.route_drop_shipping')
        self.partner = self.env.ref('base.res_partner_9')
        self.product = self.env.ref('product.product_product_6')
        self.partner_purchase = self.env.ref('base.res_partner_4')

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
                  'price_unit': 500, 'route_id': self.route.id,
                  'purchase_partner_id': self.partner_purchase.id})], }
        sale_order = self.env['sale.order'].create(dict_vals)
        sale_order.action_button_confirm()
        purchase_order = self.env['purchase.order'].search(
            [('origin', '=', sale_order.name)])
        self.assertTrue(purchase_order)
        purchase_order.signal_workflow('purchase_confirm')
        origin = purchase_order.picking_ids.mapped('origin')[0]
        self.assertEqual(origin, sale_order.name + ':' + purchase_order.name)
