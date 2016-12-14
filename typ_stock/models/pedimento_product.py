# -*- coding: utf-8 -*-

from openerp import fields, models, api


class PedimentoProduct(models.TransientModel):
    """Class assigning landed_id according serial """

    _name = 'pedimento.product'

    lot_id = fields.Many2one('stock.production.lot', string='Lot',
                             help='select lot')
    landed_id = fields.Many2one('stock.landed.cost', string='Pedimento',
                                help='select pedimento')

    def _compute_default_product_id(self):
        """This method is responsible for defining the default product in this
        case the asset in the quant"""
        quant = 'active_id' in self._context and \
            self.env['stock.quant'].browse(self._context['active_id']) or False
        return quant and quant.product_id or False

    product_id = fields.Many2one('product.product',
                                 default=_compute_default_product_id)

    @api.multi
    def write_lot_in_quant(self):
        quant_obj = self.env['stock.quant']
        if not self.lot_id and not self.landed_id:
            return {}
        quant_obj_id = self._context['active_id']
        quant = quant_obj.browse(quant_obj_id)
        if self.lot_id:
            quant.write({'lot_id': self.lot_id.id})
        if self.landed_id:
            quant.write({'landed_id': self.landed_id.id})
        return {}
