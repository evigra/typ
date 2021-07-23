from odoo import models, fields, api


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    hr_employee_check_ids = fields.Many2many("hr.employee.check", "hr_employee_check_id", string="Checks")
    hr_beneficiary_ids = fields.One2many("hr.employee.beneficiary", "hr_employee_beneficiary_id", "Beneficiary")
    hr_reference_ids = fields.One2many("hr.employee.reference", "hr_employee_reference_id", "Reference")
    hr_auxiliar_ids = fields.One2many("hr.employee.auxiliar", "hr_employee_auxiliar_id", "Auxiliar")
    marital = fields.Selection(selection_add=[("cohabiting", "Cohabiting")])
    user_boolean = fields.Boolean(compute="_compute_get_perm")
    blood_type = fields.Char()
    curp = fields.Char("CURP")
    number = fields.Integer("Number employee")
    skype_user = fields.Char()
    leaving_date = fields.Date()
    entry_date = fields.Date()
    reason_leaving = fields.Text("Reason for leaving")
    last_degree = fields.Selection([
        ("elementary_school", "Elementary school"),
        ("middle_school", "Middle school"),
        ("high_school", "High school"),
        ("university_degree", "University degree"),
        ("truncated_career", "Truncated career"),
        ("transcript_letter", "Transcript letter"),
        ("master_degree", "Master degree"),
        ("doctorade ", "Doctorade"),
    ])
    infonavit_credit = fields.Char()
    age = fields.Integer(compute="_compute_age", readonly=True)

    @api.depends("user_id")
    def _compute_get_perm(self):
        for employee in self:
            employee.user_boolean = (
                employee.env.user.has_group("hr.group_hr_user") or employee.env.user.id == employee.user_id.id
            )

    @api.depends("birthday")
    def _compute_age(self):
        """Obtain an integer number from birthday to get age"""
        for employee in self:
            if employee.birthday:
                today_birth = fields.Date.from_string(employee.birthday)
                today = fields.Date.from_string(fields.Date.today())
                employee.age = (
                    today.year - today_birth.year - ((today.month, today.day) < (today_birth.month, today_birth.day))
                )
