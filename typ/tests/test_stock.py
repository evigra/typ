from odoo.exceptions import RedirectWarning, ValidationError
from odoo.tests import Form, tagged

from .common import TypTransactionCase


@tagged("stock")
class TestStock(TypTransactionCase):
    def setUp(self):
        super().setUp()
        self.sequence_manual_transfer = self.env.ref("typ.sequence_transfer")

    def create_manual_transfer(self, warehouse=None, route=None, **line_kwargs):
        if route is None:
            route = self.route_warehouse1_reception
        transfer = Form(self.env["stock.manual_transfer"])
        if warehouse is not None:
            transfer.warehouse_id = warehouse
        transfer.route_id = route
        transfer = transfer.save()
        self.create_manual_transfer_line(transfer, **line_kwargs)
        return transfer

    def create_manual_transfer_line(self, transfer, product=None, quantity=None):
        if product is None:
            product = self.product
        with Form(transfer) as tr, tr.transfer_line_ids.new() as line:
            line.product_id = product
            if quantity is not None:
                line.product_uom_qty = quantity

    def test_01_manual_transfer(self):
        """Test creating a manual transfer and validating it so pickings are created"""
        # Create transfer and check default values
        transfer = self.create_manual_transfer()
        expected_name = "MT/%s/%05d" % (self.today.year, self.sequence_manual_transfer.number_next_actual - 1)
        self.assertRecordValues(
            records=transfer,
            expected_values=[
                {
                    "name": expected_name,
                    "state": "draft",
                    # Warehouse set on sales team
                    "warehouse_id": self.warehouse_test1.id,
                    "picking_ids": [],
                    "procurement_group_id": False,
                }
            ],
        )

        # Validate and check pickings were created
        transfer.action_validate()
        self.assertEqual(transfer.state, "valid")
        self.assertEqual(transfer.procurement_group_id.name, expected_name)
        pickings = transfer.picking_ids
        self.assertRecordValues(
            records=pickings.move_line_ids,
            expected_values=[
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 1.0,
                    "location_id": self.location_vendors.id,
                    "location_dest_id": self.warehouse_test1.lot_stock_id.id,
                    "origin": expected_name,
                    "state": "assigned",
                },
            ],
        )

        # Use action to open pickings
        action_res = transfer.action_view_pickings()
        opened_pickings = self.env[action_res["res_model"]].search(action_res["domain"])
        self.assertEqual(pickings, opened_pickings)

        # Once a transfer is validated, we shouldn't be able to delete it
        error_msg = "You can not delete a validated transfer"
        with self.assertRaisesRegex(ValidationError, error_msg):
            transfer.unlink()

        # But if it's one in draft, we should be able to delete it, even if it has lines
        draft_transfer = self.create_manual_transfer()
        draft_transfer.unlink()

    def test_02_validate_picking_with_more_products(self):
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

    def test_03_unreserve_unavailable(self):
        """Screw reserved quantity on quants on purpose

        A flow of sale and delivery but screwing reserved quantity on quants to check fixing action is triggered
        only on those quants.
        """
        # Make products available
        quant_product1 = self.inventory_adjustment(product=self.product)
        quant_product2 = self.inventory_adjustment(product=self.product_serial, lot_name="0000000000003")

        # sell products
        sale_order = self.create_sale_order(quantity=3)
        self.create_so_line(sale_order, product=self.product_serial)
        sale_order.action_confirm()
        self.assertEqual(sale_order.state, "sale")

        # Product should've been automatically reserved as there's enough stock
        picking = sale_order.picking_ids
        self.assertEqual(picking.state, "assigned")
        self.assertRecordValues(
            records=picking.move_line_ids,
            expected_values=[
                {
                    "product_id": self.product.id,
                    "product_uom_qty": 3.0,
                    "qty_done": 0.0,
                },
                {
                    "product_id": self.product_serial.id,
                    "product_uom_qty": 1.0,
                    "qty_done": 0.0,
                },
            ],
        )
        self.assertEqual(quant_product1.reserved_quantity, 3.0)
        self.assertEqual(quant_product2.reserved_quantity, 1.0)

        # Screw quants ;)
        quant_product1.reserved_quantity = 0.0
        quant_product2.reserved_quantity = 0.0

        # If we try to validate the picking, an error should be raised suggesting the action to fix quants
        error_msg = "It is not possible to unreserve more products of .* than you have in stock"
        expected_quants = quant_product1 | quant_product2
        expected_context = {"search_only_quant_ids": expected_quants.ids}
        with self.assertRaisesRegex(RedirectWarning, error_msg) as cm:
            self.immediate_transfer(picking)
        self.assertEqual(cm.exception.args[3], expected_context)

        # If the active record is the sale order, it should return the same context
        with self.assertRaisesRegex(RedirectWarning, error_msg) as cm:
            self.immediate_transfer(picking, active_record=sale_order)
        self.assertEqual(cm.exception.args[3], expected_context)

        # Run the action to fix quants, only IDs provided in context should be considered
        action = self.env["ir.actions.server"].with_context(**expected_context).browse(cm.exception.args[1])
        with self.assertSearchDomain("stock.quant", [("id", "in", expected_quants.ids)]):
            action.run()
        self.assertFalse(quant_product1.reserved_quantity)
        self.assertFalse(quant_product2.reserved_quantity)
