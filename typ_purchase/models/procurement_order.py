# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp import _, api, models


class ProcurementOrder(models.Model):

    _inherit = "procurement.order"

    @api.multi
    def make_po(self):
        """ Resolve the purchase from procurement, which may result in a new
        PO creation and a new PO line creation if it cames from a sale order,
        otherwise, can result in a modification to an existing PO and
        their lines PO.

        @return: dictionary giving for each procurement its related resolving
        PO line.
        """
        if not (self.rule_id.action == 'buy' and
                self.rule_id.route_id.sale_selectable):
            return super(ProcurementOrder, self).make_po()

        res = {}
        po_obj = self.env['purchase.order']
        seq_obj = self.env['ir.sequence']
        company = self.env['res.users'].browse(self._uid).company_id
        for procurement in self:
            ctx_company = dict(self._context or {},
                               force_company=procurement.company_id.id)
            partner = self._get_product_supplier(procurement)
            if not partner:
                self.message_post(
                    [procurement.id],
                    _('There is no supplier associated to product %s') %
                    (procurement.product_id.name))
                res[procurement.id] = False
            else:
                schedule_date = self._get_purchase_schedule_date(
                    procurement, company)
                purchase_date = self._get_purchase_order_date(
                    procurement, company, schedule_date)
                line_vals = self.with_context(
                    ctx_company)._get_po_line_values_from_proc(
                        procurement, partner, company, schedule_date)
                name = seq_obj.get('purchase.order') or \
                    _('PO: %s') % procurement.name
                partner_product_pricelist_pur = \
                    partner.property_product_pricelist_purchase
                po_vals = {
                    'name': name,
                    'origin': procurement.origin,
                    'partner_id': partner.id,
                    'location_id': procurement.location_id.id,
                    'picking_type_id': procurement.rule_id.picking_type_id.id,
                    'pricelist_id': partner_product_pricelist_pur.id,
                    'currency_id': partner_product_pricelist_pur and
                    partner_product_pricelist_pur.currency_id.id or
                    procurement.company_id.currency_id.id,
                    'date_order':
                    purchase_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                    'company_id': procurement.company_id.id,
                    'fiscal_position':
                    po_obj.with_context(
                        dict(self._context,
                             company_id=procurement.company_id.id)
                    ).onchange_partner_id(
                        partner.id)['value']['fiscal_position'],
                    'payment_term_id':
                    partner.property_supplier_payment_term.id or False,
                    'dest_address_id': procurement.partner_dest_id.id,
                }
                po_id = self.sudo(SUPERUSER_ID).with_context(
                    dict(self._context, company_id=po_vals['company_id'])
                ).create_procurement_purchase_order(
                    procurement, po_vals, line_vals)
                po_line_id = po_obj.browse(po_id).order_line[0].id
                procurement.message_post(
                    body=_("Draft Purchase Order created"))

                res[procurement.id] = po_line_id
                procurement.write({'purchase_line_id': po_line_id})
        return res
