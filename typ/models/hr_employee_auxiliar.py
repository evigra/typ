from odoo import fields, models


class HrEmployeeAuxiliar(models.Model):
    _name = "hr.employee.auxiliar"
    _description = "TODO: Once talk with the team describe it for v14.0"

    name = fields.Char()
    address = fields.Char()
    telephone = fields.Char()
    hr_employee_auxiliar_id = fields.Many2one("hr.employee", "Employee")
