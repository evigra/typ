# -*- encoding: utf-8 -*- 
from openerp.osv import osv, fields
STATUS = [
    ('Revision','Revision'),
    ('Aclaracion','Aclaracion'),
    ('Facturado','Facturado'),
    ('En Agencia Aduanal','En agencia Aduanal'),
    ('Backorder','Backorder'),
    ('Cerrado','Cerrado')
]
""" Heredamos la clase padre res.partner y creamos un campo de tipo many2one para relacionarlo con
    con el objeto hr.employee para acceder a él.
    """
class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
        'comprador_id': fields.many2one("hr.employee", "Comprador", searchable=True),
    }
""" Creamos un campo de tipo related, accedemos a partner_id de la tabla res.partner y seleccionamos el campo a utilizar de res.partner
(comprador_id)referenciamos el id de la tabla hr.employee mediante relation.
    """
class supplier_assignment(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    _columns = {
        'comprador_id': fields.related('partner_id','comprador_id',string="Comprador", type="many2one", relation="hr.employee", readonly=True, store=True),
    }
supplier_assignment()

# Agregamos al modelo purchase.order el campo create_date
class fecha_elaboracion(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

    _columns = {
        'create_date' : fields.datetime('Fecha Elaboracion', readonly=True),
        'estado': fields.selection(STATUS,'Status', store=True),
    }
fecha_elaboracion()
