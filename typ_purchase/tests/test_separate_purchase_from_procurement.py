# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestSeparatePurchaseFromProcurement(TransactionCase):

    def setUp(self):
        super(TestSeparatePurchaseFromProcurement, self).setUp()
        self.route = self.env.ref('stock.route_warehouse0_mto')
        self.route_buy = self.env.ref('purchase.route_warehouse0_buy')
        self.route_buy.pull_ids.write(
            {'group_propagation_option': 'propagate'})
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_delivery_02')
        self.pricelist = self.env.ref('product.list0')
        self.env.user.sale_team_id.sale_pricelist_id = self.pricelist.id
        self.line_vals = {
            'name': self.product.name, 'product_id': self.product.id,
            'product_uom_qty': 1, 'product_uom': self.product.uom_id.id,
            'price_unit': 500, 'route_id': self.route.id, }
        self.dict_vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, self.line_vals)], }
        self.sale_order_1 = self.env['sale.order'].create(
            self.dict_vals.copy())
        self.sale_order_1.action_confirm()

    def test_00_no_join_purchase_orders(self):
        """Test that when field join_po is FALSE in company, the new purchase
        must be NOT join with old purchase with similar characteristics.
        """
        purchase_order = self.env['purchase.order'].search(
            [('origin', '=', self.sale_order_1.name)])
        self.assertTrue(purchase_order)
        self.dict_vals.update({'name': 'Test Sale'})
        sale_order = self.env['sale.order'].create(self.dict_vals)
        sale_order.action_confirm()
        # A new purchase must has been created
        self.assertTrue(self.env['purchase.order'].search(
            [('origin', '=', sale_order.name)]))
        # The old purchase_order must has preserved their origin
        self.assertTrue(purchase_order.origin, self.sale_order_1.name)
