import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['stock.move.line'].search([
            ('picking_id.state', '!=', 'done')
        ])._compute_sorting()
