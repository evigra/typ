# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime
from openerp.osv import osv
from openerp import _
from openerp.addons.l10n_mx_facturae_report.report.invoice_facturae_html \
    import InvoiceFacturaeHtml as Parser


_logger = logging.getLogger(__name__)


class InvoiceReport(Parser):

    def __init__(self, cr, uid, name, context):
        super(InvoiceReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'eval': eval,
            'datetime': datetime,
            '_': _,
        })
        self.context = context


class InvoiceReportPDF(osv.AbstractModel):

    # _name = `report.` + `report_name`
    _name = 'report.account.invoice.qweb.report'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'typ.report_electronic_invoice'
    _wrapped_report_class = InvoiceReport
