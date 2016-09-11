# -*- coding: utf-8 -*-

from openerp.tests import common


class TestTypStock(common.TransactionCase):

    def setUp(self):
        super(TestTypStock, self).setUp()

        product = self.env.ref('product.product_product_6')
        partner = self.env.ref('base.res_partner_9')
        warehouse = self.env.ref('typ_stock.whr_test_01')
        route = self.env.ref('typ_stock.stock_location_route_test_1')

        dict_vals = {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'picking_policy': 'direct',
            'pricelist_id': self.ref('product.list0'),
            'warehouse_id': warehouse.id,
            'order_line': [
                (0, 0, {'name': product.name, 'product_id': product.id,
                        'product_uom_qty': 3, 'product_uom': product.uom_id.id,
                        'price_unit': product.list_price, 'route_id': route.id,
                        })], }

        self.sale_order = self.env['sale.order'].create(dict_vals)
        self.sale_order.action_button_confirm()

        self.first_pick = [pick for pick in self.sale_order.picking_ids if
                           pick.state == 'confirmed'][0]
        self.first_pick.force_assign()

        transfer_obj = self.env['stock.transfer_details']
        ctx = {
            "active_id": self.first_pick.id,
            "active_ids": [self.first_pick.id],
            "active_model": "stock.picking",
        }
        self.wizard_transfer_id = transfer_obj.with_context(ctx).create({
            'picking_id': self.first_pick.id, })
