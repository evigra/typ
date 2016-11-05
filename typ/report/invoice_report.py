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
            'get_model_object': self._get_model_object,
            'get_sale_order': self._get_sale_order,
            'get_type_payment_term': self._get_type_payment_term,
            '_': _,
        })
        self.context = context

    def _get_model_object(self, o):
        """Returns the Record related to the source model object. For example,
        the account.invoice object associated to the report."""
        model_obj = None
        if o.id_source:
            model_obj = self.pool.get(o.model_source).browse(
                self.cr, self.uid, o.id_source)
        return model_obj

    def _get_sale_order(self, id_invoice):
        """Returns the sale object Record associated to the invoice"""
        order_brw = self.pool.get('sale.order').search(
            self.cr, self.uid, [('invoice_ids', 'in', [id_invoice])])
        id_order = order_brw[0] if len(order_brw) else False
        order_obj = None
        if id_order:
            order_obj = self.pool.get('sale.order').browse(
                self.cr, self.uid, id_order)
        return order_obj

    def _get_type_payment_term(self, invoice):
        """Returns the type payment term in readable form"""
        tpt = invoice.type_payment_term
        selection = dict(invoice._columns['type_payment_term'].selection)
        return _(selection[tpt])


class InvoiceReportPDF(osv.AbstractModel):

    # _name = `report.` + `report_name`
    _name = 'report.account.invoice.qweb.report'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'typ.report_electronic_invoice'
    _wrapped_report_class = InvoiceReport
