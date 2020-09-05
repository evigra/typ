from openerp import api, fields, models


class ProjectIssueAttribute(models.Model):

    _name = "project.issue.attribute"

    name = fields.Char(string="Attribute", required=True)


class ProjectIssueAttributeType(models.Model):

    _name = "project.issue.attribute_type"

    name = fields.Char(string="Attribute Type", required=True)
    attribute_id = fields.Many2one('project.issue.attribute', required=True)


class ProjectIssue(models.Model):

    _inherit = 'project.issue'

    attribute_id = fields.Many2one('project.issue.attribute',
                                   track_visibility='onchange',
                                   Help="issue's attribute")
    attribute_type_id = fields.Many2one('project.issue.attribute_type',
                                        track_visibility='onchange')
    section_id = fields.Many2one('crm.case.section', default=lambda self:
                                 self.env.user.default_section_id,
                                 track_visibility='onchange')
    project_id = fields.Many2one('project.project', string="Responsible Area",
                                 track_visibility='onchange')
    customer_id = fields.Many2one('res.partner', domain=[
        ('customer', '=', True), ], track_visibility='onchange')
    supplier_id = fields.Many2one('res.partner', domain=[
        ('supplier', '=', True), ], track_visibility='onchange')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')],
                                track_visibility='onchange')
    corrective_action = fields.Text()
    preventive_proposal = fields.Text()
    solution = fields.Text()
    date_deadline = fields.Date(track_visibility='onchange')
    date_closed = fields.Datetime(readonly=True)

    @api.multi
    @api.onchange('attribute_id')
    def _onchange_attribute_id(self):
        self.attribute_type_id = False
        if self.attribute_id:
            return {'domain': {'attribute_type_id': [('attribute_id', '=',
                                                      self.attribute_id.id)]}}
