# -*- coding: utf-8 -*-

from openerp.tests.common import TransactionCase


class TestPartnerPricelist(TransactionCase):

    def setUp(self):
        super(TestPartnerPricelist, self).setUp()
        self.pricelist_sale_1 = self.env['product.pricelist'].create({
            'name': 'Pricelist Sale 1', 'type': 'sale'})
        self.pricelist_purchase_1 = self.env['product.pricelist'].create({
            'name': 'Pricelist Purchase 1', 'type': 'purchase'})
        self.pricelist_sale_2 = self.env['product.pricelist'].create({
            'name': 'Pricelist Sale 2', 'type': 'sale'})
        self.pricelist_purchase_2 = self.env['product.pricelist'].create({
            'name': 'Pricelist Purchase 2', 'type': 'purchase'})
        self.pricelist_sale_3 = self.env['product.pricelist'].create({
            'name': 'Pricelist Sale 3', 'type': 'sale'})
        self.pricelist_purchase_3 = self.env['product.pricelist'].create({
            'name': 'Pricelist Purchase 3', 'type': 'purchase'})
        self.partner_sale = self.env.ref('base.res_partner_9')
        self.partner_purchase = self.env.ref('base.res_partner_4')
        self.warehouse = self.env.ref('stock.warehouse0')
        self.dict_vals_sale = {
            'partner_id': self.partner_sale.id,
            'partner_invoice_id': self.partner_sale.id,
            'partner_shipping_id': self.partner_sale.id,
            'warehouse_id': self.warehouse.id,
        }
        self.dict_vals_purchase = {
            'partner_id': self.partner_purchase.id,
            'pricelist_id': self.ref('product.list0'),
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
        }

    def test_00_partner_sale_without_pricelist_ids(self):
        """In this test the sale order created does not must have pricelist
        domain.
        """
        self.partner_sale.write({
            'property_product_pricelist': self.pricelist_sale_1.id, })
        self.assertEqual(self.partner_sale.property_product_pricelist,
                         self.pricelist_sale_1)
        self.assertEqual(len(self.partner_sale.pricelist_ids), 0)

        sale_order = self.env['sale.order'].sudo().create(self.dict_vals_sale)
        res = sale_order.get_domain_pricelist()
        self.assertEqual(res, None)

    def test_10_partner_sale_with_pricelist_ids(self):
        """In this test the sale order created  must have 2 pricelist in
        domain.
        """
        self.partner_sale.write({
            'property_product_pricelist': self.pricelist_sale_1.id,
            'pricelist_ids': [(6, 0, [self.pricelist_sale_2.id,
                                      self.pricelist_sale_3.id])]})
        self.assertEqual(self.partner_sale.property_product_pricelist,
                         self.pricelist_sale_1)
        self.assertEqual(len(self.partner_sale.pricelist_ids), 2)

        sale_order = self.env['sale.order'].sudo().create(self.dict_vals_sale)
        res = sale_order.get_domain_pricelist()
        self.assertEqual(len(res['domain']['pricelist_id'][0][2]), 2)

    def test_20_partner_purchase_without_pricelist_ids(self):
        """In this test the purchase order created does not must have pricelist
        domain.
        """
        self.partner_purchase.write({
            'property_product_pricelist_purchase':
            self.pricelist_purchase_1.id, })
        self.assertEqual(
            self.partner_purchase.property_product_pricelist_purchase,
            self.pricelist_purchase_1)
        self.assertEqual(len(self.partner_purchase.pricelist_ids), 0)

        purchase_order = self.env['purchase.order'].sudo().create(
            self.dict_vals_purchase)
        res = purchase_order.get_domain_pricelist()
        self.assertEqual(res, None)

    def test_30_partner_purchase_with_pricelist_ids(self):
        """In this test the purchase order created must have 2 pricelist in
        domain.
        """
        self.partner_purchase.write({
            'property_product_pricelist_purchase':
            self.pricelist_purchase_1.id,
            'pricelist_ids': [(6, 0, [self.pricelist_purchase_2.id,
                                      self.pricelist_purchase_3.id])]})
        self.assertEqual(
            self.partner_purchase.property_product_pricelist_purchase,
            self.pricelist_purchase_1)
        self.assertEqual(len(self.partner_purchase.pricelist_ids), 2)

        purchase_order = self.env['purchase.order'].sudo().create(
            self.dict_vals_purchase)
        res = purchase_order.get_domain_pricelist()
        self.assertEqual(len(res['domain']['pricelist_id'][0][2]), 2)
