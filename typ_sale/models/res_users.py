# -*- coding: utf-8 -*-

from openerp import api, models


class ResUsers(models.Model):

    _inherit = "res.users"

    @api.multi
    def write(self, values):
        res = super(ResUsers, self).write(values)
        if 'sale_team_ids' in values:
            self.clear_caches()
        return res
