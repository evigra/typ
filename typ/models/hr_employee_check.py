from odoo import models, fields


class HrEmployeeCheck(models.Model):
    _name = "hr.employee.check"
    _description = "TODO: Once talk with the team describe it for v14.0"

    name = fields.Char()
    doc_type = fields.Selection([("RD", "Recruitment documents"), ("CD", "Company documents")])
