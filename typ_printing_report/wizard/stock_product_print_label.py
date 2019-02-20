# coding: utf-8

from odoo import api, fields, models


class PrintLabel(models.TransientModel):

    _name = 'stock.print_label'
    _description = 'Print product label'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    report_id = fields.Many2one('ir.actions.report', 'Label report',
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
            data = {'qty': self.qty}
        return self.report_id.report_action(self.product_id.ids, data)
