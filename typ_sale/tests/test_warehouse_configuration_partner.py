# -*- coding: utf-8 -*-

from openerp.exceptions import ValidationError
from openerp.tests.common import TransactionCase


class TestWarehouseConfigurationPartner(TransactionCase):

    def setUp(self):
        super(TestWarehouseConfigurationPartner, self).setUp()
        self.partner_1 = self.env['res.partner'].create({
            'name': 'Partner_1'})
        self.partner_2 = self.env['res.partner'].create({
            'name': 'Partner_2'})
        self.warehouse_1 = self.env['stock.warehouse'].create({
            'name': 'Warehouse_1', 'code': 'WH1'})
        self.warehouse_2 = self.env['stock.warehouse'].create({
            'name': 'Warehouse_2', 'code': 'WH2'})
        self.user_1 = self.env['res.users'].create({
            'name': 'User_1', 'login': 'user_1@test.com',
            'password': '123456'})
        self.user_2 = self.env['res.users'].create({
            'name': 'User_2', 'login': 'user_2@test.com',
            'password': '123456'})
        self.pricelist = self.env.ref('product.list0')

    def test_00_constraint_repeat_warehouse(self):
        """Test that raise is generate when it try to create a warehouse
        configuration in a partner with warehouse already existing in other
        configuration in the same partner
        """
        self.env['res.partner.warehouse'].create({
            'warehouse_id': self.warehouse_1.id, 'user_id': self.user_1.id,
            'credit_limit': 100.00, 'partner_id': self.partner_1.id})
        msg = ".*There is more than one configuration for warehouse.*"
        new_conf = self.env['res.partner.warehouse'].create({
            'warehouse_id': self.warehouse_1.id,
            'user_id': self.user_1.id,
            'credit_limit': 100.00, })
        with self.assertRaisesRegexp(ValidationError, msg):
            self.partner_1.write({'res_warehouse_ids': [(4, new_conf.id)]})

    def test_10_onchange_warehouse_id_sale_order(self):
        """Test when change warehouse_id in a sale_order, salesman must be
        update with a respective configuration
        """
        self.env['res.partner.warehouse'].create({
            'warehouse_id': self.warehouse_1.id, 'user_id': self.user_1.id,
            'credit_limit': 100.00, 'partner_id': self.partner_1.id})

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'partner_invoice_id': self.partner_1.id,
            'partner_shipping_id': self.partner_1.id,
            'pricelist_id': self.pricelist.id,
            'warehouse_id': self.warehouse_1.id})
        sale_order.get_salesman_from_warehouse_config()
        self.assertEqual(sale_order.user_id, self.user_1)

        self.env['res.partner.warehouse'].create({
            'warehouse_id': self.warehouse_2.id, 'user_id': self.user_2.id,
            'credit_limit': 100.00, 'partner_id': self.partner_1.id})
        sale_order.write({'warehouse_id': self.warehouse_2.id})
        sale_order.get_salesman_from_warehouse_config()
        self.assertEqual(sale_order.user_id, self.user_2)

    def test_20_onchange_partner_id_sale_order(self):
        """Test when change partner_id in a sale_order, salesman must be
        update with a respective configuration
        """
        self.env['res.partner.warehouse'].create({
            'warehouse_id': self.warehouse_1.id, 'user_id': self.user_1.id,
            'credit_limit': 100.00, 'partner_id': self.partner_1.id})

        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_1.id,
            'partner_invoice_id': self.partner_1.id,
            'partner_shipping_id': self.partner_1.id,
            'pricelist_id': self.pricelist.id,
            'warehouse_id': self.warehouse_1.id})
        sale_order.get_salesman_from_warehouse_config()
        self.assertEqual(sale_order.user_id, self.user_1)

        self.env['res.partner.warehouse'].create({
            'warehouse_id': self.warehouse_1.id, 'user_id': self.user_2.id,
            'credit_limit': 100.00, 'partner_id': self.partner_2.id})
        sale_order.write({'partner_id': self.partner_2.id})
        sale_order.get_salesman_from_warehouse_config()
        self.assertEqual(sale_order.user_id, self.user_2)
