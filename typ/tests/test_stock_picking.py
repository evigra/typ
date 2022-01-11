from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import TypTransactionCase


@tagged("stock_picking")
class TestSale(TypTransactionCase):
    def test_01_validate_picking_with_more_products(self):
        # create 2 products
        partner_1 = self.customer = self.env["res.partner"].create(
            {
                "name": "Partner Test 1",
                "vat": "XEXX010101000",
            }
        )
        product_1 = self.env["product.product"].create(
            {
                "name": "product_1",
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
                "barcode": "product_1",
            }
        )
        supplier_location = self.env.ref("stock.stock_location_suppliers")
        stock_location = self.env.ref("stock.stock_location_stock")
        picking_type_out = self.env.ref("stock.picking_type_out")
        picking_1 = self.env["stock.picking"].create(
            {
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "partner_id": partner_1.id,
                "picking_type_id": picking_type_out.id,
            }
        )
        move_1 = self.env["stock.move"].create(
            {
                "name": product_1.name,
                "product_id": product_1.id,
                "product_uom_qty": 1,
                "product_uom": product_1.uom_id.id,
                "picking_id": picking_1.id,
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "origin": "MPS",
            }
        )
        move_1.quantity_done = 5
        picking_1.move_line_ids.product_uom_qty = 2
        with self.assertRaises(ValidationError):
            picking_1.button_validate()

        picking_2 = self.env["stock.picking"].create(
            {
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "partner_id": partner_1.id,
                "picking_type_id": picking_type_out.id,
            }
        )
        move_2 = self.env["stock.move"].create(
            {
                "name": product_1.name,
                "product_id": product_1.id,
                "product_uom_qty": 1,
                "product_uom": product_1.uom_id.id,
                "picking_id": picking_2.id,
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "origin": "MPS",
            }
        )
        move_2.quantity_done = 2
        picking_2.move_line_ids.product_uom_qty = 2
        self.assertTrue(picking_2.button_validate())
