from .common import TestTypStock


class TestSerialWizardByLotId(TestTypStock):
    def test_00_serial_wizard_by_lot_id(self):
        self.product_test = self.env["product.product"].create(
            {"name": "Test product", "list_price": 130.0, "track_all": True, "lot_unique_ok": True}
        )
        self.update_product_qty()

        extra_values = {
            "picking_type_id": self.picking_type_out.id,
        }

        location_src = self.picking_type_out.default_location_src_id.id
        location_dest = self.picking_type_out.default_location_dest_id.id
        line = {
            "product_id": self.product_test.id,
            "product_uom_qty": 2,
            "product_uom": self.product_test.uom_id.id,
            "price_unit": self.product_test.list_price,
            "picking_type_id": self.picking_type_out.id,
            "location_id": location_src,
            "location_dest_id": location_dest,
        }

        picking = self.create_picking_default(extra_values, line)
        stock_serial_id = (
            self.env["stock.serial"]
            .with_context({"active_id": picking.move_lines[0].id, "active_model": "stock.move"})
            .create({})
        )

        # Warning message must be displayed when try to add the same lot twice
        self.env["stock.serial.line"].with_context({"move_id": picking.move_lines[0].id}).create(
            {"lot_id": self.lot_1.id, "serial_id": stock_serial_id.id}
        )
        self.assertFalse(stock_serial_id.onchange_serial())

        self.env["stock.serial.line"].with_context({"move_id": picking.move_lines[0].id}).create(
            {"lot_id": self.lot_1.id, "serial_id": stock_serial_id.id}
        )
        self.assertIn("warning", stock_serial_id.onchange_serial())
