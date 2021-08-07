from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    daily_salary = fields.Float()
    integrate_daily_salary = fields.Float()
