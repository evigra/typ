from odoo import fields, models


class HrEmployeeReference(models.Model):
    _name = "hr.employee.reference"
    _description = "TODO: Once talk with the team describe it for v14.0"

    name = fields.Char()
    friendly = fields.Char()
    hr_employee_reference_id = fields.Many2one("hr.employee", "Employee")
