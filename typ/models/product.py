from odoo import models, fields, api

# from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP  -> TODO: review on v14.0


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_highlight = fields.Boolean(
        default=False,
        string="Highlight Product",
        help="Manual selector for featured products",
    )

    # @api.model  # TODO: Reimplement this with core feature.
    # def _get_price_taxed(self, untaxed_price):
    #     self.ensure_one()
    #     taxes = []
    #     for tax in self.taxes_id:
    #         taxes += (tax.sudo().compute_all(untaxed_price, currency=None, quantity=1.0, 
    # product=self, partner=None, ) .get("taxes") )
    #     taxed_price = sum([tax.get("amount") for tax in taxes]) + untaxed_price
    #     return taxed_price

    # def is_favorite(self):  # TODO: Reimplement this with the core feature
    #     self.ensure_one()
    #     result_wish = self.env["user.wishlist"].search(
    #         [
    #             ("product_template_id", "=", self.id),
    #             ("user_id", "=", self.env.uid),
    #         ],
    #         limit=1,
    #     )
    #     return bool(result_wish)

    # TODO: review in 14.0
    # def price_compute(self, price_type, uom=False, currency=False,
    #                   company=False):
    #     if self.env.context.get('other_pricelist'):
    #         return 0
    #     return super(ProductTemplate, self).price_compute(
    #         price_type, uom=uom, currency=currency, company=company)


class ProductProduct(models.Model):
    _inherit = "product.product"

    # TODO: Check if this does not cause performance problems since at update
    # process will update this fields when updating product, stock and typ
    # modules Ticket 6289
    description = fields.Text(
        translate=True,
        help="A precise description of the Product, used only for internal "
        "information purposes.",
    )
    description_purchase = fields.Text(
        "Purchase Description",
        translate=True,
        help="A description of the Product that you want to communicate "
        "to your vendors. This description will be copied to every "
        "Purchase Order, Receipt and Vendor Bill/Credit Note.",
    )
    description_sale = fields.Text(
        "Sale Description",
        translate=True,
        help="A description of the Product that you want to communicate to "
        "your customers. This description will be copied to every Sales Order,"
        " Delivery Order and Customer Invoice/Credit Note",
    )
    description_picking = fields.Text("Description on Picking", translate=True)
    description_pickingout = fields.Text(
        "Description on Delivery Orders", translate=True
    )
    description_pickingin = fields.Text(
        "Description on Receptions", translate=True
    )
    sale_line_warn_msg = fields.Text("Message for Sales Order Line")
    purchase_line_warn_msg = fields.Text("Message for Purchase Order Line")

    route_ids = fields.Many2many("stock.location.route", "stock_route_product_product", "product_id", "route_id",
                                 "Routes", domain="[('product_selectable', '=', True)]",
                                 help="Depending on the modules installed, this will allow you to define the route of "
                                 "the product: whether it will be bought, manufactured, MTO/MTS,...")

    product_warehouse_ids = fields.One2many("product.stock.warehouse", "product_id", "Storage location",
        help="Configure storage location" " to each warehouse")

    # TODO: Check if module lifecycle can be used here in v14.0
    state = fields.Selection([
        ("draft", "In Development"),
        ("sellable", "Normal"),
        ("end", "End of Lifecycle"),
        ("obsolete", "Obsolete"),
        ("temporary", "Temporary"),
        ("support", "Support"),
    ], help="State of lifecycle of the product.")

    project_or_replacement = fields.Selection(
        [("project", "Project"), ("replacement", "Replacement"), ("projrepl", "Project Replacement")],
        help="The product is usually used for a new PROJECT, is used "
        "to REPLACE some component or is used for both.",
    )
    ref_ac = fields.Selection(
        [("ref", "Refrigeration"), ("ac", "AC"), ("refac", "Refrigeration AC")],
        string="Refrigeration/AC",
        help="The product is used for Refrigeration, Air Conditioning or both.",
    )
    final_market = fields.Selection(
        [
            ("res", "RES"),
            ("com", "COM"),
            ("ind", "IND"),
            ("res_com", "RES COM"),
            ("res_ind", "RES IND"),
            ("com_ind", "COM IND"),
            ("res_com_ind", "RES COM IND"),
        ],
        help="The final market to which the product is directed in general is "
        "residential (RES), Commercial (COM), Industrial (IND), "
        "the last three, only residential and commercial, only residential "
        "and industrial or commercial and industrial.",
    )
    main_customer_activity = fields.Selection([
        ("con", "CON"),
        ("emp", "EMP"),
        ("may", "MAY"),
        ("con_emp", "CON EMP"),
        ("con_may", "CON MAY"),
        ("emp_may", "EMP MAY"),
        ("con_emp_may", "CON EMP MAY"),
    ],
        help="The activity of the client that uses this product is mainly "
        "Contractor (CON), Company (EMP), Wholesaler (MAY), Contractor but "
        "also a company, company but also a wholesaler, contractor but "
        "also wholesaler or all of the above.",
    )
    wait_time = fields.Selection(
        [("nulo", "Nulo"), ("nday", "Next day"), ("nurg", "Not urgent")],
        help="The delivery time according to the priority and importance of "
        "the product is Null if it can not wait, Next Day if the time is "
        "moderate and No Urgent if we can wait to have it.",
    )
    type_of_client = fields.Selection(
        [
            ("co", "CO"),
            ("cr", "CR"),
            ("cp", "CP"),
            ("esp", "ESP"),
            ("cn", "CN"),
            ("emb", "EMB"),
            ("sup", "SUP"),
            ("ali", "ALI"),
            ("may", "MAY"),
            ("otros", "OTROS"),
            ("cocr", "CO CR"),
            ("cocp", "CO CP"),
            ("cnesp", "CN ESP"),
            ("cocrmay", "CO CR MAY"),
            ("ccec", "CO CP ESP CN"),
            ("esao", "EMB SUP ALI OTROS"),
            ("cccec", "CO CR CP ESP CN"),
            ("ccecm", "CO CP ESP CN MAY"),
            ("ccesa", "CO CR EMB SUP ALI"),
            ("cccecm", "CO CR CP ESP CN MAY"),
            ("cccecesao", "CO CR CP ESP CN EMB SUP ALI OTROS"),
            ("todos", "TODOS"),
        ],
        help="Types of customers, defined in the target market.",
    )
    price_sensitivity = fields.Selection(
        [
            ("ns", "Insensitive"),
            ("ps", "Little sensitive"),
            ("n", "Neutral"),
            ("as", "Something sensitive"),
            ("ms", "Very sensitive"),
        ],
        help="Field to know how much the price of the product impacts the " "customers decision to purchase.",
    )
    product_nature = fields.Selection(
        [("commodity", "Commodity"), ("specialty", "Specialty"), ("normal", "Normal")],
        help="A Commodity product is a product that almost all suppliers "
        "handle, its main attribute is the price. A Specialty product is "
        "one with a unique or specific purpose, "
        "Normal product that is handled from stock.",
    )
    product_market_type = fields.Many2one("product.market.type", ondelete="set null", index=True)

    alternative_variant_ids = fields.Many2many(
        "product.product",
        "variant_alternative_rel",
        "src_id",
        "dest_id",
        string="Alternative variants",
        help="Alternative variants" " to offer the customer",
    )

    # @api.model  # TODO: This is really necessary this will be a performance problematic method I think
    # def name_search(self, name="", args=None, operator="ilike", limit=80):
    #     res = super().name_search(name, args=args, operator=operator, limit=limit)
    #     if not limit or len(res) >= limit:
    #         limit = (limit - len(res)) if limit else False
    #     if not name or len(res) >= limit:
    #         return res
    #     limit -= len(res)
    #     products = self.search(
    #         [("attribute_value_ids.name", operator, name)], limit=limit
    #     )
    #     if not products:
    #         return res
    #     res.extend(products.name_get())
    #     return res

