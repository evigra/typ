from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSaleChangePrice(TransactionCase):

    def setUp(self):
        super(TestSaleChangePrice, self).setUp()
        self.group_modify_price_unit = self.env.ref(
            'typ_sale.res_group_modify_price_sale')
        self.partner_camp = self.env['res.partner'].create({
            'name': 'Test partner',
        })
        self.prod_ipadmini = self.env.ref('product.product_product_6')
        self.prod_service = self.env.ref(
            'product.membership_2_product_template')

        self.dict_vals_line = {
            'name': self.prod_ipadmini.name,
            'product_id': self.prod_ipadmini.id,
            'product_uom_qty': 1, 'product_uom': self.prod_ipadmini.uom_id.id,
            'price_unit': self.prod_ipadmini.list_price, }
        self.dict_vals = {
            'partner_id': self.partner_camp.id,
            'order_line': [(0, 0, self.dict_vals_line)],
        }
        self.demo_user = self.env.ref('base.user_demo')
        self.sale = self.env['sale.order'].sudo(self.demo_user).create(
            self.dict_vals)

    def test_00_sale_change_price_with_allowed_group(self):
        """Changing the price belonging to the group
        """
        self.demo_user.write({
            'groups_id': [(4, self.group_modify_price_unit.id)]})

        self.sale.order_line.price_unit = 200.0
        self.sale.order_line._onchange_price_unit()
        self.assertEqual(self.sale.order_line.price_unit, 200.0)

    def test_01_sale_change_price_without_allowed_group(self):
        """Prevent changing the price without not belonging to the group
        """
        with self.assertRaises(ValidationError):
            self.sale.order_line.price_unit = 200
            self.sale.order_line._onchange_price_unit()

    def test_02_sale_change_price_with_allowed_category(self):
        """Change price unit by allowed category of product
        """
        self.prod_ipadmini.categ_id.allow_change_price_sale = True
        self.sale.order_line.price_unit = 200
        self.sale.order_line._onchange_price_unit()
        self.assertEqual(self.sale.order_line.price_unit, 200.0)

    def test_03_sale_change_price_type_service(self):
        """Change price unit for service type product
        """
        order_line = self.env['sale.order.line'].new({
            'order_id': self.sale.id,
            'product_id': self.prod_service.id,
        })
        order_line.price_unit = 200
        order_line._onchange_price_unit()
        self.assertEqual(order_line.price_unit, 200.0)
