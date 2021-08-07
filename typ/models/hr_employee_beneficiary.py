from odoo import fields, models


class HrEmployeeBeneficiary(models.Model):
    _name = "hr.employee.beneficiary"
    _description = "TODO: describe it for v14.0, note, This should be to a partner in the next iteraton"

    name = fields.Char()
    address = fields.Char()
    rfc = fields.Char()
    percentage = fields.Char()
    hr_employee_beneficiary_id = fields.Many2one("hr.employee", "Employee")
