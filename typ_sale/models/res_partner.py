# coding: utf-8

import collections

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = 'res.partner'

    res_warehouse_ids = fields.One2many(
        comodel_name='res.partner.warehouse', inverse_name='partner_id',
        string='Warehouse configuration', help='Configurate salesman and'
        ' credit limit to each warehouse')

    @api.multi
    @api.constrains('res_warehouse_ids')
    def unique_conf_partner_warehouse(self):
        for res in self:
            warehouse_ids = [res_wh.warehouse_id for res_wh in
                             res.res_warehouse_ids]
            dict_values = dict(collections.Counter(warehouse_ids))
            for key in dict_values.keys():
                if dict_values[key] > 1:
                    raise ValidationError(
                        _('There is more than one configuration for warehouse'
                          ' %s. It must have only one configuration for each'
                          ' warehouse') % (key.name))
