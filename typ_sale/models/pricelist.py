# coding: utf-8

from __future__ import division
from itertools import chain
import logging

from odoo import api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):

    _inherit = 'product.product'

    state = fields.Selection(
        [('draft', 'In Development'),
         ('sellable', 'Normal'),
         ('end', 'End of Lifecycle'),
         ('obsolete', 'Obsolete'),
         ('support', 'Support')],
        help='State of lifecycle of the product.'
    )
    project_or_replacement = fields.Selection(
        [('project', 'Project'),
         ('replacement', 'Replacement'),
         ('projrepl', 'Project Replacement')],
        help='The product is usually used for a new PROJECT, is used '
        'to REPLACE some component or is used for both.'
    )
    ref_ac = fields.Selection(
        [('ref', 'Refrigeration'),
         ('ac', 'AC'),
         ('refac', 'Refrigeration AC')],
        string='Refrigeration/AC',
        help='The product is used for Refrigeration, Air Conditioning or both.'
    )
    final_market = fields.Selection(
        [('res', 'RES'),
         ('com', 'COM'),
         ('ind', 'IND'),
         ('res_com', 'RES COM'),
         ('res_ind', 'RES IND'),
         ('com_ind', 'COM IND'),
         ('res_com_ind', 'RES COM IND')],
        help='The final market to which the product is directed in general is '
        'residential (RES), Commercial (COM), Industrial (IND), '
        'the last three, only residential and commercial, only residential '
        'and industrial or commercial and industrial.'
    )
    main_customer_activity = fields.Selection(
        [('con', 'CON'),
         ('emp', 'EMP'),
         ('may', 'MAY'),
         ('con_emp', 'CON EMP'),
         ('con_may', 'CON MAY'),
         ('emp_may', 'EMP MAY'),
         ('con_emp_may', 'CON EMP MAY')],
        help='The activity of the client that uses this product is mainly '
        'Contractor (CON), Company (EMP), Wholesaler (MAY), Contractor but '
        'also a company, company but also a wholesaler, contractor but '
        'also wholesaler or all of the above.'
    )
    wait_time = fields.Selection(
        [('nulo', 'Nulo'),
         ('nday', 'Next day'),
         ('nurg', 'Not urgent')],
        help='The delivery time according to the priority and importance of '
        'the product is Null if it can not wait, Next Day if the time is '
        'moderate and No Urgent if we can wait to have it.'
    )
    type_of_client = fields.Selection(
        [('co', 'CO'),
         ('cr', 'CR'),
         ('cp', 'CP'),
         ('esp', 'ESP'),
         ('cn', 'CN'),
         ('emb', 'EMB'),
         ('sup', 'SUP'),
         ('ali', 'ALI'),
         ('may', 'MAY'),
         ('otros', 'OTROS'),
         ('cocr', 'CO CR'),
         ('cocp', 'CO CP'),
         ('cnesp', 'CN ESP'),
         ('cocrmay', 'CO CR MAY'),
         ('ccec', 'CO CP ESP CN'),
         ('esao', 'EMB SUP ALI OTROS'),
         ('cccec', 'CO CR CP ESP CN'),
         ('ccecm', 'CO CP ESP CN MAY'),
         ('ccesa', 'CO CR EMB SUP ALI'),
         ('cccecm', 'CO CR CP ESP CN MAY'),
         ('cccecesao', 'CO CR CP ESP CN EMB SUP ALI OTROS'),
         ('todos', 'TODOS')],
        help='Types of customers, defined in the target market.'
    )
    price_sensitivity = fields.Selection(
        [('ns', 'Insensitive'),
         ('ps', 'Little sensitive'),
         ('n', 'Neutral'),
         ('as', 'Something sensitive'),
         ('ms', 'Very sensitive')],
        help='Field to know how much the price of the product impacts the '
        'customers decision to purchase.'
    )
    product_nature = fields.Selection(
        [('commodity', 'Commodity'),
         ('specialty', 'Specialty'),
         ('normal', 'Normal')],
        help='A Commodity product is a product that almost all suppliers '
        'handle, its main attribute is the price. A Specialty product is '
        'one with a unique or specific purpose, '
        'Normal product that is handled from stock.'
    )
    product_market_type = fields.Many2one('product.market.type',
                                          ondelete='set null', index=True)

    alternative_variant_ids = fields.Many2many(
        'product.product', 'variant_alternative_rel', 'src_id', 'dest_id',
        string='Alternative variants', help='Alternative variants'
        ' to offer the customer'
    )

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False,
                      company=False):
        if self.env.context.get('other_pricelist'):
            return 0
        return super(ProductProduct, self).price_compute(
            price_type, uom=uom, currency=currency, company=company)


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False,
                      company=False):
        if self.env.context.get('other_pricelist'):
            return 0
        return super(ProductTemplate, self).price_compute(
            price_type, uom=uom, currency=currency, company=company)


class ProductMarketType(models.Model):
    _name = 'product.market.type'

    name = fields.Char(required=True)


class PricelistItem(models.Model):

    _inherit = 'product.pricelist.item'

    _order = 'sequence asc'

    sequence = fields.Integer(default=5)


class Pricelist(models.Model):

    _inherit = 'product.pricelist'

    # pylint: disable=R1260
    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False,
                            uom_id=False):
        """ Low-level method - Mono pricelist, multi products
        Returns: dict{product_id: (price, suitable_rule) for the given
        pricelist}

        If date in context: Date of the pricelist (%Y-%m-%d)

        :param products_qty_partner: list of typles products, quantity, partner
        :param datetime date: validity date
        :param ID uom_id: intermediate unit of measure
        """
        date = date or self._context.get('date') or fields.Date.context_today(
            self)
        uom_id = (
            self._context['uom']
            if not uom_id and self._context.get('uom') else uom_id)
        if uom_id:
            # rebrowse with uom if given
            products = [
                item[0].with_context(uom=uom_id)
                for item in products_qty_partner]
            products_qty_partner = [
                (products[index], data_struct[1], data_struct[2])
                for index, data_struct in enumerate(products_qty_partner)]
        else:
            products = [item[0] for item in products_qty_partner]

        if not products:
            return {}

        categ_ids = {}
        for product in products:
            categ = product.categ_id
            while categ:
                categ_ids[categ.id] = True
                categ = categ.parent_id
        categ_ids = list(categ_ids)

        is_product_template = products[0]._name == "product.template"
        if is_product_template:
            prod_tmpl_ids = [tmpl.id for tmpl in products]
            # all variants of all products
            prod_ids = [
                p.id for p in list(chain.from_iterable(
                    [t.product_variant_ids for t in products]))]
        else:
            prod_ids = [product.id for product in products]
            prod_tmpl_ids = [
                product.product_tmpl_id.id for product in products]

        # Load all rules
        self._cr.execute(
            '''
            SELECT
                item.id
            FROM
                product_pricelist_item AS item
            LEFT JOIN
                product_category AS categ ON item.categ_id = categ.id
            WHERE
                (item.product_tmpl_id IS NULL OR
                 item.product_tmpl_id = any(%s)) AND
                (item.product_id IS NULL OR item.product_id = any(%s)) AND
                (item.categ_id IS NULL OR item.categ_id = any(%s)) AND
                (item.pricelist_id = %s) AND
                (item.date_start IS NULL OR item.date_start<=%s) AND
                (item.date_end IS NULL OR item.date_end>=%s)
            ORDER BY
                item.sequence asc,
                item.applied_on,
                item.min_quantity desc,
                categ.parent_left desc''',
            (prod_tmpl_ids, prod_ids, categ_ids, self.id, date, date))

        item_ids = [x[0] for x in self._cr.fetchall()]
        items = self.env['product.pricelist.item'].browse(item_ids)
        results = {}
        for product, qty, partner in products_qty_partner:
            results[product.id] = 0.0
            suitable_rule = False

            qty_uom_id = self._context.get('uom') or product.uom_id.id
            qty_in_product_uom = qty
            if qty_uom_id != product.uom_id.id:
                try:
                    qty_in_product_uom = self.env['product.uom'].browse(
                        [self._context['uom']])._compute_quantity(
                            qty, product.uom_id)
                except UserError:
                    _logger.warning('Passing error computing quantities')

            price = 0.0

            price_uom = self.env['product.uom'].browse([qty_uom_id])
            for rule in items:
                if (rule.min_quantity and
                        qty_in_product_uom < rule.min_quantity):
                    continue
                if is_product_template:
                    if (rule.product_tmpl_id and
                            product.id != rule.product_tmpl_id.id):
                        continue
                    if (rule.product_id and not
                            (product.product_variant_count == 1 and
                             product.product_variant_id == rule.product_id)):
                        continue
                else:
                    if (rule.product_tmpl_id and
                            product.product_tmpl_id != rule.product_tmpl_id):
                        continue
                    if rule.product_id and product.id != rule.product_id.id:
                        continue

                if rule.categ_id:
                    cat = product.categ_id
                    while cat:
                        if cat.id == rule.categ_id.id:
                            break
                        cat = cat.parent_id
                    if not cat:
                        continue

                if rule.base == 'pricelist' and rule.base_pricelist_id:
                    price_tmp = (
                        rule.base_pricelist_id.with_context(
                            other_pricelist=True)._compute_price_rule(
                                [(product, qty, partner)])[product.id][0])
                    price = rule.base_pricelist_id.currency_id.compute(
                        price_tmp, self.currency_id, round=False)
                    if not price:
                        continue
                else:
                    price = product.price_compute(rule.base)[product.id]

                convert_to_price_uom = (
                    lambda price: product.uom_id._compute_price(price,
                                                                price_uom))

                if price is not False:
                    if rule.compute_price == 'fixed':
                        price = convert_to_price_uom(rule.fixed_price)
                    elif rule.compute_price == 'percentage':
                        price = (
                            price - (price *
                                     (rule.percent_price / 100))) or 0.0
                    else:
                        # complete formula
                        price_limit = price
                        price = (
                            price - (price *
                                     (rule.price_discount / 100))) or 0.0
                        if rule.price_round:
                            price = tools.float_round(
                                price, precision_rounding=rule.price_round)

                        if rule.price_surcharge:
                            price_surcharge = convert_to_price_uom(
                                rule.price_surcharge)
                            price += price_surcharge

                        if rule.price_min_margin:
                            price_min_margin = convert_to_price_uom(
                                rule.price_min_margin)
                            price = max(price, price_limit + price_min_margin)

                        if rule.price_max_margin:
                            price_max_margin = convert_to_price_uom(
                                rule.price_max_margin)
                            price = min(price, price_limit + price_max_margin)
                    suitable_rule = rule
                break
            # Final price conversion into pricelist currency
            if (suitable_rule and
                    suitable_rule.compute_price != 'fixed' and
                    suitable_rule.base != 'pricelist'):
                price = product.currency_id.compute(
                    price, self.currency_id, round=False)

            if not price and not self.env.context.get('other_pricelist'):
                price = product.price_compute('list_price')[product.id]

            results[product.id] = (
                price, suitable_rule and suitable_rule.id or False)

        return results
