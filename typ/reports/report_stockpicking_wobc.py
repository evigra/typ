from collections import defaultdict

from odoo import models


class StockPickingOperationsiReportWobc(models.AbstractModel):
    _name = "report.typ_.report_picking_wobc"
    _description = "TODO: Once talk with the team describe it for v14.0"

    def get_report_values(self, docids, data=None):
        docs = self.env["stock.picking"].browse(docids)
        return {
            "doc_ids": docs.ids,
            "doc_model": "stock.picking",
            "docs": docs,
            "data": data,
            "lines_category_three": self.get_line_by_category_three,
        }

    def get_line_by_category_three(self, doc):
        moves = doc.mapped("move_lines")
        group_move = defaultdict(lambda: self.env["stock.move"])
        for move in moves:
            complete_name = move.product_id.categ_id.complete_name
            name_three = complete_name.rsplit("/", 3)
            if len(name_three) > 3:
                name_three.pop(0)
            name_three.pop()
            complete_name_three = "/".join(name_three).strip()
            group_move[complete_name_three] |= move
        return sorted(group_move.items())
