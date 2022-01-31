from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    hr_employee_check_ids = fields.Many2many(
        "hr.employee.check",
        "hr_employee_check_id",
        string="Checks",
        groups="hr.group_hr_user",
    )
    hr_beneficiary_ids = fields.One2many(
        "hr.employee.beneficiary",
        "hr_employee_beneficiary_id",
        string="Beneficiary",
        groups="hr.group_hr_user",
    )
    hr_reference_ids = fields.One2many(
        "hr.employee.reference",
        "hr_employee_reference_id",
        string="Reference",
        groups="hr.group_hr_user",
    )
    hr_auxiliar_ids = fields.One2many(
        "hr.employee.auxiliar",
        "hr_employee_auxiliar_id",
        string="Auxiliar",
        groups="hr.group_hr_user",
    )
    blood_type = fields.Selection(
        selection=[
            ("A-", "A-"),
            ("A+", "A+"),
            ("B-", "B-"),
            ("B+", "B+"),
            ("AB-", "AB-"),
            ("AB+", "AB+"),
            ("O-", "O-"),
            ("O+", "O+"),
        ],
        groups="hr.group_hr_user",
    )
    curp = fields.Char(string="CURP", groups="hr.group_hr_user")
    number = fields.Integer(string="Number employee", groups="hr.group_hr_user")
    leaving_date = fields.Date(groups="hr.group_hr_user")
    entry_date = fields.Date(groups="hr.group_hr_user")
    reason_leaving = fields.Text("Reason for leaving", groups="hr.group_hr_user")
    last_degree = fields.Selection(
        selection=[
            ("elementary_school", "Elementary school"),
            ("middle_school", "Middle school"),
            ("high_school", "High school"),
            ("university_degree", "University degree"),
            ("truncated_career", "Truncated career"),
            ("transcript_letter", "Transcript letter"),
            ("master_degree", "Master degree"),
            ("doctorade ", "Doctorade"),
        ],
        groups="hr.group_hr_user",
    )
    infonavit_credit = fields.Char(groups="hr.group_hr_user")
    age = fields.Integer(
        compute="_compute_age",
        groups="hr.group_hr_user",
    )

    @api.depends("birthday", "tz")
    def _compute_age(self):
        """Obtain an integer number from birthday to get age"""
        for employee in self:
            tz = employee.tz or employee.user_id.tz or self.env.user.tz
            employee = employee.with_context(tz=tz)
            today = fields.Date.context_today(employee)
            birthday = employee.birthday or today
            employee.age = relativedelta(today, birthday).years
