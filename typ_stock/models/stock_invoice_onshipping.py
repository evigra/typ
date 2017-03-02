# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.tools.safe_eval import safe_eval


class StockInvoiceOnshipping(models.TransientModel):
    """Class inherit wizard to open invoice from pickings
    """

    _inherit = "stock.invoice.onshipping"

    @api.multi
    def open_invoice(self):
        action = super(StockInvoiceOnshipping, self).open_invoice()
        if action is True or self.journal_type != 'sale':
            return action
        act_dom = safe_eval(action.get('domain'))
        if act_dom:
            act = act_dom[0]
        # check the invoice_ids
        if len(act[2]) > 1:
            return action
        act_context = safe_eval(action.get('context'))
        view_id = list()
        view_id.append(self.env.ref("account.invoice_form").id)
        action.pop('view_ids')
        res_id = act[2]
        return {
            'name': action['name'],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_id': res_id[0],
            'res_model': 'account.invoice',
            'context': act_context,
            'type': action['type'],
            'nodestroy': True,
            'target': 'current',
        }
