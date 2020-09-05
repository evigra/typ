from openerp import api, fields, models
import openerp.addons.decimal_precision as dp


class StockTransferDetails(models.TransientModel):

    _inherit = 'stock.transfer_details'

    @api.model
    def default_get(self, values):
        res = super(StockTransferDetails, self).default_get(values)
        picking = self.env['stock.picking'].browse(
            self._context.get('active_id'))
        for item in res.get('item_ids', []):
            item['supplier_code'] = self.get_supplier_code(
                picking, item['product_id'])
            item['expected_quantity'] = item['quantity']
            if picking.location_id.usage == "supplier" \
                    and picking.location_dest_id.usage == 'internal'\
                    and not item['lot_id']:
                item['quantity'] = 0.0
        return res

    @api.multi
    def get_supplier_code(self, picking, product_id):
        suppliers = self.env['product.product'].browse(product_id).seller_ids.\
            filtered(lambda r: r.name == picking.partner_id)
        for supplier in suppliers:
            if supplier.product_code:
                return supplier.product_code
        return


class StockTransferDetailsItems(models.TransientModel):

    _inherit = 'stock.transfer_details_items'

    supplier_code = fields.Char()
    expected_quantity = fields.Float(digits=dp.get_precision
                                     ('Product Unit of Measure'), default=0.0,
                                     readonly=True)
