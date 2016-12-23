# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) info@vauxoo.com
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from openerp import api, models


class AccountInvoice(models.Model):

    _inherit = 'account.invoice'

    @api.model
    def get_human_value(self, field_name, selection_option):
        """Convert technical key to value to show in selection human readable
        for the user.
        :param field_name: selection field name
        :param selection_option: the technical value of actual_state
        :return: string with the value that will be shown in the user
        """
        data = dict(self.fields_get().get(field_name).get('selection'))
        return data.get(selection_option, '')
