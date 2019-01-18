from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    map_location = fields.Text(
        string='Google Maps Location',
        help='Embeded url from google maps')
