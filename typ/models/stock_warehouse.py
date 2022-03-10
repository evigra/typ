from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    is_cedis = fields.Boolean(
        string="Is CEDIS?",
        copy=False,
        help="Indicates wheter this warehouse is a distribution center.",
    )

    def _load_records(self, data_list, update=False):
        """Create external IDs for locations and picking types, for convenience"""
        # Applies only for new records
        existing_records = [self.env.ref(v.get("xml_id"), False) for v in data_list]
        existing_records = self.browse(w.id for w in existing_records if w)
        res = super()._load_records(data_list, update)

        new_records = res - existing_records
        for warehouse in new_records:
            warehouse_extid = warehouse.get_external_id()[warehouse.id]
            location_extid = warehouse_extid + "_location"
            location_view_extid = warehouse_extid + "_location_view"
            pick_type_in_extid = warehouse_extid + "_pick_type_in"
            pick_type_out_extid = warehouse_extid + "_pick_type_out"
            route_reception_extid = warehouse_extid + "_route_reception"
            route_delivery_extid = warehouse_extid + "_route_delivery"
            self.env["ir.model.data"]._update_xmlids(
                [
                    {
                        "xml_id": location_extid,
                        "record": warehouse.lot_stock_id,
                        "noupdate": True,
                    },
                    {
                        "xml_id": location_view_extid,
                        "record": warehouse.view_location_id,
                        "noupdate": True,
                    },
                    {
                        "xml_id": pick_type_in_extid,
                        "record": warehouse.in_type_id,
                        "noupdate": True,
                    },
                    {
                        "xml_id": pick_type_out_extid,
                        "record": warehouse.out_type_id,
                        "noupdate": True,
                    },
                    {
                        "xml_id": route_reception_extid,
                        "record": warehouse.reception_route_id,
                        "noupdate": True,
                    },
                    {
                        "xml_id": route_delivery_extid,
                        "record": warehouse.delivery_route_id,
                        "noupdate": True,
                    },
                ],
            )

        return res
