from openerp.osv import osv, fields
class account_invoice(osv.osv):
    _inherit ='account.invoice'
    _columns = {
      'rel_invoice': fields.boolean('Relacionada Factura Cliente', help='Indica que esta Nota de Credito esta relacionada con una Factura de Cliente'),
      }
    _defaults = {
    	'rel_invoice': True,
    }