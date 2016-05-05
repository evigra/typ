# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
# ----------------------------------------------------
# Picking In
# ----------------------------------------------------
# class stock_picking_in(orm.Model):
#     _inherit = "stock.picking.in"

#     def set_to_draft(self, cr, uid, ids, *args):
#         if not len(ids):
#             return False
#         move_obj = self.pool.get('stock.move')
#         self.write(cr, uid, ids, {'state': 'draft'})
#         wf_service = netsvc.LocalService("workflow")
#         for p_id in ids:
#             moves = move_obj.search(cr, uid, [('picking_id', '=', p_id)])
#             move_obj.write(cr, uid, moves, {'state': 'draft'})
#             # Deleting the existing instance of workflow for PO
#             wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
#             wf_service.trg_create(uid, 'stock.picking', p_id, cr)
#         for (id, name) in self.name_get(cr, uid, ids):
#             message = _("Picking '%s' has been set in draft state.") % name
#             self.log(cr, uid, id, message)
#         return True

# # ----------------------------------------------------
# # Picking Out
# # ----------------------------------------------------
# class stock_picking_out(orm.Model):
#     _inherit = "stock.picking.out"

#     def set_to_draft(self, cr, uid, ids, *args):
#         if not len(ids):
#             return False
#         move_obj = self.pool.get('stock.move')
#         self.write(cr, uid, ids, {'state': 'draft'})
#         wf_service = netsvc.LocalService("workflow")
#         for p_id in ids:
#             moves = move_obj.search(cr, uid, [('picking_id', '=', p_id)])
#             move_obj.write(cr, uid, moves, {'state': 'draft'})
#             # Deleting the existing instance of workflow for PO
#             wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
#             wf_service.trg_create(uid, 'stock.picking', p_id, cr)
#         for (id, name) in self.name_get(cr, uid, ids):
#             message = _("Picking '%s' has been set in draft state.") % name
#             self.log(cr, uid, id, message)
#         return True

# ----------------------------------------------------
# Picking Internal
# ----------------------------------------------------
class stock_picking(orm.Model):
    _inherit = "stock.picking"

    def set_to_draft(self, cr, uid, ids, *args):
        if not len(ids):
            return False
        move_obj = self.pool.get('stock.move')
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for p_id in ids:
            moves = move_obj.search(cr, uid, [('picking_id', '=', p_id)])
            move_obj.write(cr, uid, moves, {'state': 'draft'})
            # Deleting the existing instance of workflow for PO
            wf_service.trg_delete(uid, 'stock.picking', p_id, cr)
            wf_service.trg_create(uid, 'stock.picking', p_id, cr)
        for (id, name) in self.name_get(cr, uid, ids):
            message = _("Picking '%s' has been set in draft state.") % name
            self.log(cr, uid, id, message)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
