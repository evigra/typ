from odoo import models, fields


class ProductProduct(models.Model):

    _inherit = "product.product"

    report_id = fields.Many2one("ir.actions.report", "Label report", domain="[('model','=','product.product')]")
    normalized_barcode = fields.Boolean(
        default=True,
        string="Normalized",
        help="The supplier will provide a "
        "proper barcode if True if not "
        "then you can generate your own "
        "barcode",
    )

    def generate_barcode(self, *args, **kw):
        self.ensure_one()
        if self.normalized_barcode:
            return True
        return super().generate_barcode(*args, **kw)


class ProductCategory(models.Model):

    _inherit = "product.category"

    report_id = fields.Many2one("ir.actions.report", "Label report", domain="[('model','=','product.product')]")
