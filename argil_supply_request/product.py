# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
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
##############################################################################

from openerp.osv import osv, fields


class product_template(osv.osv):
    _inherit="product.template"

    _columns = {
        'procure_method': fields.selection([('make_to_stock','Make to Stock'),
                                            ('make_to_order','Make to Order'),
                                            ('make_to_supply_request','Make to Supply Request')], 
                                           'Procurement Method', required=True, help="Make to Stock: "\
                                           "When needed, the product is taken from the stock or we wait"\
                                           " for replenishment. \nMake to Order: When needed, the product"\
                                           " is purchased or produced.\n Make to Supply Request: When needed,"\
                                           " supply request is created to distribution center and we wait"),
    }
product_template()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: