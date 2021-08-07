from odoo import api, fields, models


class HrEmployeeIndicator(models.Model):
    _name = "hr.employee.indicator"
    _description = "Employee Indicator"

    name = fields.Char(required=True)
    indicator_code = fields.Char("Code")
    description = fields.Text()
    weight = fields.Float()
    weighted_weight = fields.Float()
    metric_type = fields.Selection(
        selection=[
            ("greater", "Greater equal to"),
            ("less", "Less equal to"),
            ("between", "Between range"),
        ],
        required=True,
        default="greater",
        help="Metric of the Indicator, [Greater equal to], " "[Less equal to] and [Between range]",
    )
    metric_great = fields.Float()
    metric_less = fields.Float()
    metric = fields.Char(compute="_compute_metric")

    @api.depends("metric_type")
    def _compute_metric(self):
        metric = ""
        for indicator in self:
            if indicator.metric_type == "less":
                metric = str(indicator.metric_less)
            elif indicator.metric_type == "greater":
                metric = str(indicator.metric_great)
            else:
                metric = str(indicator.metric_great) + " to " + str(indicator.metric_less)
            indicator.update(
                {
                    "metric": metric,
                }
            )
