
from openerp import models, fields
import openerp.addons.typ_sale.models.res_partner as typ_sale_partner


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
    importance = fields.Selection(typ_sale_partner.IMPORTANCE)
    potential_importance = fields.Selection(typ_sale_partner.POTENTIAL)
    business_activity = fields.Selection(typ_sale_partner.BUSINESS_ACTIVITY)
    partner_type = fields.Selection(typ_sale_partner.CLIENT_TYPE)
    dealer = fields.Selection(typ_sale_partner.DEALER_TYPE)
    region = fields.Selection(typ_sale_partner.REGION)
    date_month = fields.Char()

    def _select(self):
        return super(AccountInvoiceReport, self)._select() + """,
            sub.importance,
            sub.potential_importance,
            sub.business_activity,
            sub.partner_type,
            sub.dealer,
            sub.region,
            date_part('month', sub.date) as date_month
        """

    def _sub_select(self):
        return super(AccountInvoiceReport, self)._sub_select() + """,
            partner.importance,
            partner.potential_importance,
            partner.business_activity,
            partner.partner_type,
            partner.dealer,
            partner.region
        """

    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + """,
            partner.importance,
            partner.potential_importance,
            partner.business_activity,
            partner.partner_type,
            partner.dealer,
            partner.region
        """
