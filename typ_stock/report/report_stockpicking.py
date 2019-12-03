from odoo import api, models


class StockPickingOperationsiReport(models.AbstractModel):
    _name = 'report.stock.report_picking'

    @api.multi
    def get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'data': data,
            'docs': docs,
        }
