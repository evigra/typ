from lxml import etree

from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    usage = fields.Char("Action Usage")

    def _render_qweb_pdf(self, docids, data=None):
        """Generate a PDF and returns it.

        If the action configured on the report is server, it prints the
        generated document as well.
        """
        if not docids:
            docids = self._context.get("active_ids")
        document, doc_format = super()._render_qweb_pdf(docids, data=data)
        behaviour = self.behaviour()
        printer = behaviour.pop("printer", None)
        if self.usage == "zebra" and printer:
            arch, _ = self._render_qweb_html(docids, data=data)
            tree = etree.fromstring(arch)
            code = tree.xpath("//div[@class='code']")
            res = code[0].text if code else ""
            res = "\n".join([line.strip() for line in res.split("\n") if line.strip()])
            res += "\n"
            return res.encode(), doc_format
        return document, doc_format
