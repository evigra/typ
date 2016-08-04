# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
##############################################################################


from openerp.osv import osv, fields

class res_partner(osv.osv):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _columns = {
    'addenda_femsa': fields.boolean('Adenda FEMSA', help='Define Si se le Generara Addenda a Este Cliente'),
    'no_proveedor_addenda': fields.char('No. Proveedor', size=128, help='No. de Proveedor Asignado por el Cliente para la Adenda'),
    'addenda_soriana': fields.boolean('Adenda SORIANA', help='Define Si se le Generara Addenda a Este Cliente'),

    }

    _defaults = {

    }
res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
