from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    
    _inherit = "sale.advance.payment.inv"

    def _create_invoice(self, order, so_line, amount):
        res = super()._create_invoice(order, so_line, amount)
        res.get_payment_term()
        return res
