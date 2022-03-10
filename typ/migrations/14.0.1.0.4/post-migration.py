import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    set_warehouse_cedis_field(cr)


def set_warehouse_cedis_field(cr):
    """Set the "Is CEDIS?" field to the CEDIS warehouse"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    warehouse_cedis = env["stock.warehouse"].search([("name", "=", "ALMACEN CEDIS")])
    warehouse_cedis.write({"is_cedis": True})
    _logger.info("Field is_cedis was set to warehouses with IDs %s", warehouse_cedis.ids)
