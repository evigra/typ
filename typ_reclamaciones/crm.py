# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields
class gestion_reclamaciones(osv.osv):
    _name = 'crm.claim'
    _inherit = 'crm.claim'
    _columns = {
        'cantidad': fields.char('Cantidad',required=True),
        'product_id': fields.many2one('product.product','Producto', required=True),
        'prodlot_id': fields.many2one('stock.production.lot', 'No. de serie'),
        'supplier_id': fields.many2one('res.partner','Proveedor', required=True),
        'numero': fields.char('Factura', required=True),
        'orden_compra': fields.many2one('purchase.order', 'Orden de compra'),
    }