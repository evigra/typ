# coding: utf-8

from openerp import api, fields, models


class PrintLabel(models.TransientModel):

    _name = 'stock.print_label'
    _description = 'Print product label'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    report_id = fields.Many2one('ir.actions.report.xml', 'Label report',
                                required=True,
                                domain="[('model','=','product.product')]")
    qty = fields.Integer('Quantity', required=True,
                         help="Quantity of labels to print")

    @api.model
    def default_get(self, fields_list):
        res = super(PrintLabel, self).default_get(fields_list)
        move = self.env['stock.move'].browse(self.env.context['active_id'])
        report = (move.product_id.report_id.id or
                  move.product_id.categ_id.report_id.id or
                  move.company_id.report_id.id)
        res.update({
            'product_id': move.product_id.id,
            'qty': int(move.product_uom_qty),
            'report_id': report
            })
        return res

    @api.multi
    def print_label(self):
        data = False
        if self.report_id.usage == 'zebra':
            data = {'ids': self.product_id.ids, 'qty': self.qty}
        return self.env["report"].with_context(
            active_ids=self.product_id.ids,
            active_model='product.product').get_action(
                self.product_id, self.report_id.report_name, data)


class ProductProduct(models.Model):

    _inherit = 'product.product'

    report_id = fields.Many2one('ir.actions.report.xml', 'Label report',
                                domain="[('model','=','product.product')]")


class ProductCategory(models.Model):

    _inherit = 'product.category'

    report_id = fields.Many2one('ir.actions.report.xml', 'Label report',
                                domain="[('model','=','product.product')]")


class ResCompany(models.Model):

    _inherit = 'res.company'

    report_id = fields.Many2one('ir.actions.report.xml', 'Label report',
                                domain="[('model','=','product.product')]")


class StockMove(models.Model):

    _inherit = "stock.move"

    normalized_barcode = fields.Boolean(
        related='product_id.normalized_barcode')
    location_usage = fields.Selection(related='location_id.usage')
