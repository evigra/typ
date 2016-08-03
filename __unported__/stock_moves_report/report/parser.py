###########################################################################
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) OpenERP.
#    All Rights Reserved
###############Credits######################################################
#    Coded by: carlos Mexia cmexia
#    Planified by: Cmexia
#    Audited by:
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################

import time
from openerp.report import report_sxw
import mx.DateTime


class moves_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(moves_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({'time': time,})

report_sxw.report_sxw(
    'report.stock_moves_report',
    'stock.move',
    'addons/stock_moves_report/report/stock_moves.rml',
    parser=moves_parser,
    header='internal landscape',
)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
