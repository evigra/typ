# -*- coding: utf-8 -*-

from openerp import api, models


class ReportZebraProduct(models.AbstractModel):

    _name = 'report.typ_printing_report.product_label_zebra_view'

    @api.model
    def render_html(self, docids, data=None):
        if data is None:
            data = {}

        datas = {
            'docs': self.env['product.product'].browse(
                data.get('ids', docids)),
            'qty': data.get('qty', 1)
        }
        return self.env['report'].render(
            'typ_printing_report.product_label_zebra_view', datas)
