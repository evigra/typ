
from openerp import models, api


class ProductTemplate(models.Model):

    _inherit = "product.template"

    @api.multi
    def get_product_accounts(self, fiscal_pos=None):
        location_obj = self.env['stock.location']
        sale_team_obj = self.env['crm.team']

        res = super(ProductTemplate, self).get_product_accounts(fiscal_pos)

        loc_id = self._context.get('location')
        if loc_id:
            location_id = location_obj.browse(loc_id)
            warehouse_id = location_obj.get_warehouse(location_id)
            sale_team_id = sale_team_obj.search(
                [('default_warehouse', '=', warehouse_id)], limit=1)
            journal_id = sale_team_id.journal_stock_id
            if journal_id:
                res['stock_journal'] = journal_id.id
        return res
