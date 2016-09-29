# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestPurchaseFromSaleOrder(TransactionCase):

    def setUp(self):
        super(TestPurchaseFromSaleOrder, self).setUp()
        self.route = self.env.ref('stock_dropshipping.route_drop_shipping')
        self.partner = self.env.ref('base.res_partner_9')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.product = self.env.ref('product.product_product_6')
        self.partner_purchase = self.env.ref('base.res_partner_4')

    def test_00_special_sale_order(self):
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
        self.assertEqual(sale_order.order_line.purchase_partner_id,
                         purchase_order.partner_id)
