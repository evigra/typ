# coding: utf-8

from openerp import fields, models, api


class CrmTeam(models.Model):

    _inherit = "crm.team"

    sale_phone = fields.Char(
        string="Phone",
        help="Phone for contact sale team")
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal position',
        help='It indicates the fiscal position'
        ' to be used when sale order is created')

    @api.multi
    def write(self, values):
        res = super(CrmTeam, self).write(values)
        if 'member_ids' in values or 'journal_team_ids' in values:
            self.clear_caches()
        return res
