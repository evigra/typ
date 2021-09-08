from odoo import models


class StockPickingOperationsiReport(models.AbstractModel):
    _name = "report.stock.report_picking"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def _get_report_values(self, docids, data=None):
        docs = self.env["stock.picking"].browse(docids)
        return {
            "doc_ids": docs.ids,
            "doc_model": "stock.picking",
            "data": data,
            "docs": docs,
        }
