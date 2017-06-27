# coding: utf-8

from openerp import fields, models


class CrmCaseSection(models.Model):

    _inherit = "crm.case.section"

    sale_phone = fields.Char(
        string="Phone",
        help="Phone for contact sale team")
