# coding: utf-8
# Copyright 2016 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime
from openerp import _
from openerp.osv import osv
from openerp.addons.l10n_mx_facturae_report.report.invoice_facturae_html \
    import InvoiceFacturaeHtml as Parser
from openerp.tools.safe_eval import safe_eval


_logger = logging.getLogger(__name__)


class InvoiceReport(Parser):

    def __init__(self, cr, uid, name, context):
        super(InvoiceReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'eval': safe_eval,
            'datetime': datetime,
            'get_model_object': self._get_model_object,
            'get_sale_order': self._get_sale_order,
            '_': _,
            'get_payment_method': self._get_payment_method,
            'get_invoice_by_uuid': self._get_invoice_by_uuid,
        })

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
        id_order = order_brw[0] if order_brw else False
        order_obj = None
        if id_order:
            order_obj = self.pool.get('sale.order').browse(
                self.cr, self.uid, id_order)
        return order_obj

    def _get_payment_method(self, payment_method):
        """Return the name of payment method"""
        payment_obj = self.pool.get('pay.method')
        payment = payment_obj.search(
            self.cr, self.uid, [('code', '=', payment_method)], limit=1)
        payment = payment_obj.browse(self.cr, self.uid, payment)
        return '%s %s' % (
            payment.code, payment.name) if payment else payment_method

    def _get_invoice_by_uuid(self, uuid):
        """Search the invoice that have the UUID provided"""
        if not uuid:
            return ''
        invoice_obj = self.pool.get('account.invoice')
        inv = invoice_obj.search(self.cr, self.uid,
                                 [('cfdi_folio_fiscal', '=', uuid)])
        inv = invoice_obj.browse(self.cr, self.uid, inv)
        return inv.number if inv else ''


class InvoiceReportPDF(osv.AbstractModel):

    # _name = `report.` + `report_name`
    _name = 'report.account.invoice.qweb.report'

    # this inheritance will allow to render this particular report
    _inherit = 'report.abstract_report'
    _template = 'typ.report_electronic_invoice'
    _wrapped_report_class = InvoiceReport
