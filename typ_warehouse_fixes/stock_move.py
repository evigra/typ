# -*- encoding: utf-8 -*-
from openerp.osv import osv, fields
class stock_move(osv.osv):
    _inherit = 'stock.move'
    def comparate_stock_location(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.location_id!=obj.location_dest_id:
                res[obj.id]=False
            if obj.location_id==obj.location_dest_id:
                res[obj.id]=True
        return res
    _columns = {
        'consulta': fields.function(comparate_stock_location, type='boolean', string="Movimientos", store=True)
    }
    _default = {
        'consulta': comparate_stock_location
    }

# class stock_picking_out(osv.osv):
#     _inherit = 'stock.picking.out'
#     def new_state_filter(self, cr, uid, ids, state, arg, context=None):
#         res = {}
#         for obj in self.browse(cr,uid,ids, context=context):
#             if obj.state=='assigned':
#                 for line in obj.move_lines:
#                     if line.state=='confirmed':
#                         res[obj.id]=True
#             else:
#                 res[obj.id]=False
#         return res

#     _columns = {
#         'availability_filter': fields.function(new_state_filter, type='boolean', string="Esperando Disponibilidad - Partidas", store=True)
#     }
#     _default = {
#         'availability_filter': new_state_filter
#     }
class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    def new_state_filter(self, cr, uid, ids, state, arg, context=None):
        res = {}
        for obj in self.browse(cr,uid,ids, context=context):
            if obj.state=='assigned':
                for line in obj.move_lines:
                    if line.state=='confirmed':
                        res[obj.id]=True
            else:
                res[obj.id]=False
        return res

    _columns = {
        'availability_filter': fields.function(new_state_filter, type='boolean', string="Esperando Disponibilidad - Partidas", store=True)
    }
    _default = {
        'availability_filter': new_state_filter
    }
