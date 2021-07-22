from odoo import api, models


class PosReceiptReport(models.AbstractModel):
    _name = "report.point_of_sale.report_receipts"
    _description = "TODO: Once talk with the team describe it for v14.0"

    @api.model
    def render_html(self, docids, data=None):
        report = self.env["report"]
        return report.sudo().render("typ_pos.receipt_report", {"docs": self.env["pos.order"].sudo().browse(docids)})
