from odoo import api, fields, models


class HrEmployeeReport(models.Model):
    _name = "hr.employee.report"
    _description = "TODO: Once talk with the team describe it for v14.0"

    name = fields.Char(required=True, states={"done": [("readonly", True)]})
    date_report = fields.Date(
        "Date",
        required=True,
        states={"done": [("readonly", True)]},
        help="Report date, usually the first or last day of the month being evaluated.",
    )
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        default=lambda self: self.env.user.employee_ids[:1],
        help="Employee, takes it from the system user.",
    )
    department_id = fields.Many2one("hr.department", related="employee_id.department_id", store=True, readonly=True)
    job_id = fields.Many2one("hr.job", related="employee_id.job_id", store=True, readonly=True)
    report_line = fields.One2many(
        "hr.employee.report.line", "report_id", copy=True, states={"done": [("readonly", True)]}
    )
    total_weighted_weight = fields.Float(
        store=True, readonly=True, compute="_compute_ww", help="Sum of the weighted weight, must be equal to 100"
    )
    evaluation_report = fields.Float(
        store=True, readonly=True, compute="_compute_result", help="Sum of the evaluations of your indicators."
    )
    state = fields.Selection(
        selection=[
            ("draft", "Report"),
            ("done", "Revised"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        default="draft",
    )

    def action_done(self):
        return self.write({"state": "done"})

    @api.depends("report_line.weighted_weight")
    def _compute_ww(self):
        total_weighted_weight = 0.0
        for report in self:
            for line in report.report_line:
                total_weighted_weight += line.weighted_weight
            report.update(
                {
                    "total_weighted_weight": total_weighted_weight,
                }
            )

    @api.depends("report_line.evaluation")
    def _compute_result(self):
        evaluation_report = 0.0
        for report in self:
            for line in report.report_line:
                evaluation_report += line.evaluation
            report.update(
                {
                    "evaluation_report": evaluation_report,
                }
            )


class HrEmployeeReportLine(models.Model):
    _name = "hr.employee.report.line"
    _description = "TODO: Once talk with the team describe it for v14.0"

    name = fields.Char(related="indicator_id.name")
    report_id = fields.Many2one(
        "hr.employee.report", string="Report reference", required=True, index=True, ondelete="cascade", copy=True
    )
    indicator_id = fields.Many2one("hr.employee.indicator", required=True)
    indicator_code = fields.Char("Code", readonly=True, related="indicator_id.indicator_code")
    description = fields.Text(related="indicator_id.description", readonly=True)
    weight = fields.Float(
        related="indicator_id.weight",
        readonly=True,
    )
    weighted_weight = fields.Float(related="indicator_id.weighted_weight", readonly=True)
    metric = fields.Char(related="indicator_id.metric", readonly=True)
    result = fields.Float(required=True, help="The result of your evaluation of this indicator.")
    evaluation = fields.Float(
        compute="_compute_evaluation",
        help="If the metric is fulfilled, it is"
        " worth the weighted weight of the indicator, value is zero in any other case.",
    )

    @api.depends("indicator_id")
    def _compute_evaluation(self):
        for line in self:
            evaluation = 0.0
            if line.indicator_id.metric_type == "less":
                if line.result <= line.indicator_id.metric_less:
                    evaluation = line.weighted_weight
            elif line.indicator_id.metric_type == "greater":
                if line.result >= line.indicator_id.metric_great:
                    evaluation = line.weighted_weight
            else:
                if line.result >= line.indicator_id.metric_great and line.result <= line.indicator_id.metric_less:
                    evaluation = line.weighted_weight
            line.update(
                {
                    "evaluation": evaluation,
                }
            )
