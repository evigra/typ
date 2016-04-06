# -*- encoding: utf-8 -*-
#
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013 Hesa Tecnica - http://www.hesatecnica.com/
#    All Rights Reserved.
#    info hesatecnica (openerp@hesatecnica.com)
#
#    Coded by: Israel Cruz Argil (israel.cruz@hesatecnica.com)
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp


class purchase_requisition(osv.osv):
    _inherit = "purchase.requisition"

    def _get_changes_from_purchase_order(self, cr, uid, ids, context=None):
        requisition_ids = {}
        req_obj = self.pool.get('purchase.requisition')
        for r in self.pool.get('purchase.order').browse(cr, uid, ids, context=context):
            if r.origin and not r.requisition_id:
                reqs = r.origin.split(' ')
                #print "reqs: ", reqs
                res = req_obj.search(cr, uid, [('name','in',(tuple(reqs,)))], context=context)
                if res:
                    for x in res:
                        requisition_ids[x] = True
            requisition_ids[r.requisition_id.id] = True


        res = []
        if requisition_ids:
            res = req_obj.search(cr, uid, [('id','in',requisition_ids.keys())], context=context)
        return res

    def _get_incomplete_state(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            qty = 0
            for line in record.line_ids:
                qty += line.qty_remaining if line.qty_remaining > 0 else 0
            res[record.id] = True if qty else False
        return res


    _columns = {
        'incomplete'    : fields.function(_get_incomplete_state, string='Incomplete', type='boolean', multi=False, method=True,
                                           store = {'purchase.requisition': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                    'purchase.order': (_get_changes_from_purchase_order, None, 50),
                                                   }),
        }

class purchase_requisition_line(osv.osv):
    _inherit = "purchase.requisition.line"


#    def _get_changes_from_purchase_order(self, cr, uid, ids, context=None):
#        requisition_ids = {}
#        for r in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
#            requisition_ids[r.order_id.requisition_id.id] = True

#        res = []
#        if requisition_ids:
#            res = self.pool.get('purchase.requisition').search(cr, uid, [('id','in',requisition_ids.keys())], context=context)
#        return res

    def _get_product_info(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = {
                'state'                   : 'pending',
                'qty_ordered'             : 0.0,
                'qty_remaining'           : 0.0,
                }

            qty_ordered = qty_remaining =  0.0
            porders_ids = [0,0]
            for purchase in line.requisition_id.purchase_ids:
                if purchase.state not in ('draft','cancel'):
                    porders_ids.append(purchase.id)
                    for order_line in purchase.order_line:
                        if order_line.product_id.id == line.product_id.id:
                            qty_ordered += order_line.product_qty

            po_obj = self.pool.get('purchase.order')
            po_ids = po_obj.search(cr, uid, [('origin','ilike','%'+line.requisition_id.name+'%'),
                                             ('state','not in',('draft','cancel')),
                                             ('id','not in', (tuple(porders_ids,)))
                                             ], context=context)
            for merged_po in po_obj.browse(cr, uid, po_ids):
                for order_line in merged_po.order_line:
                    if order_line.product_id.id == line.product_id.id:
                        qty_ordered += order_line.product_qty

            qty_remaining = line.product_qty - qty_ordered
            state = 'pending' if qty_remaining == line.product_qty else 'partial'  if qty_remaining > 0 else 'complete'
            res[line.id] = {
                'state'                   : state,
                'qty_ordered'             : qty_ordered,
                'qty_remaining'           : qty_remaining,
                }
        return res


    _columns = {
            'state'             : fields.function(_get_product_info, type='selection', string='State', method=True, multi=True,
                                    selection= [('pending','Pending'),
                                                ('partial','Partial'),
                                                ('cancel','Cancelled'),
                                                ('complete','Complete')]),
                                            #      store = { 'purchase.requisition': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                            #                'purchase.order': (_get_changes_from_purchase_order, None, 50),
                                            #                }),
            #'purchase_order_line_ids' : fields.function(_get_product_info, type='many2many', relation='purchase.order.line', string='Purchase Order Lines'),
                                                        #store = {'purchase.order': (_get_changes_from_purchase_order, None, 50)}),
            'qty_ordered'        : fields.function(_get_product_info, string='Qty Ordered', type='float',
                                                  digits_compute= dp.get_precision('Sale Price'), method=True, multi=True),
                                             #     store = { 'purchase.requisition': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                            #                'purchase.order': (_get_changes_from_purchase_order, None, 50),
                                            #                }),
            'qty_remaining'      : fields.function(_get_product_info, string='Qty Remaining', type='float',
                                                  digits_compute= dp.get_precision('Sale Price'), method=True, multi=True),
                                                #   store = { 'purchase.requisition': (lambda self, cr, uid, ids, c={}: ids, None, 10),
                                                #            'purchase.order': (_get_changes_from_purchase_order, None, 50),
                                                #            }),

        }


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    def do_merge(self, cr, uid, ids, context=None):
        res = super(purchase_order, self).do_merge(cr, uid, ids, context=context)
        #print "res: ", res.keys()
        for new_order in res.keys():
            #print "new_order: ", new_order
            #print "old_ids: ", res[new_order]
            #print "Nueva PO: ", self.read(cr, uid, [new_order], ['name'])[0]['name']
            self.write(cr, uid, res[new_order], {'notes':'Fusionada en la Orden de Compra %s' % (self.read(cr, uid, [new_order], ['name'])[0]['name']) })

        return res
