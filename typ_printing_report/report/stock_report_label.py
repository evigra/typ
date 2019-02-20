# -*- coding: utf-8 -*-

from odoo import api, models


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

    @api.multi
    def get_report_values(self, docids, data):
        products = self.env['product.product'].browse(docids)
        return {
            'doc_ids': products.ids,
            'docs': products,
            'data': data
        }


class ReportZebraRack(models.AbstractModel):

    _name = 'report.typ_printing_report.rack_label_zebra_view'

    @api.multi
    def get_report_values(self, docids, data):
        products = self.env['product.product'].browse(docids)
        return {
            'doc_ids': products.ids,
            'docs': products,
            'data': data
        }
