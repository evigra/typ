# coding: utf-8

from openerp import fields, models


class CrmTeam(models.Model):

    _inherit = "crm.team"

    sale_phone = fields.Char(
        string="Phone",
        help="Phone for contact sale team")
