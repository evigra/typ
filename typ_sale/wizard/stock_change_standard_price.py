# -*- coding: utf-8 -*-
# © 2017 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import _, api, models


class ChangeStandardPrice(models.TransientModel):

    _inherit = 'stock.change.standard.price'

    @api.multi
    def change_price(self):

        product_obj_id = self.env.context.get('active_id')
        product_model = self.env.context.get('active_model')
        product = self.env[product_model].browse(product_obj_id)
        old_price = product.standard_price
        res = super(ChangeStandardPrice, self).change_price()
        product.message_post(body=_('Price has been modified, previous price:\
                                    %s , new price: %s') %
                             (old_price, self.new_price))
        return res
