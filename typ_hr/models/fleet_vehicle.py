

from odoo import models, fields


class Vehicle(models.Model):

    _inherit = 'fleet.vehicle'

    vehicle_manager = fields.Many2one(
        'res.partner',
        'Responsible for the vehicle',
        help='Responsible for the vehicle',
        copy=False
    )
