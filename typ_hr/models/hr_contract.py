# coding: utf-8

from openerp import models, fields


class HrContract(models.Model):

    _inherit = 'hr.contract'

    daily_salary = fields.Float()
    integrate_daily_salary = fields.Float()