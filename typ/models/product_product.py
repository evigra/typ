from odoo import fields, models

# from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP  -> TODO: review on v14.0


class ProductProduct(models.Model):
    _inherit = "product.product"

    description = fields.Text(
        translate=True,
        help="A precise description of the Product, used only for internal information purposes.",
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
    description_pickingout = fields.Text("Description on Delivery Orders", translate=True)
    description_pickingin = fields.Text("Description on Receptions", translate=True)
    sale_line_warn_msg = fields.Text("Message for Sales Order Line")
    purchase_line_warn_msg = fields.Text("Message for Purchase Order Line")
    route_ids = fields.Many2many(
        "stock.location.route",
        "stock_route_product_product",
        "product_id",
        "route_id",
        string="Routes",
        domain="[('product_selectable', '=', True)]",
        help="Depending on the modules installed, this will allow you to define the route of the product: "
        "whether it will be bought, manufactured, MTO/MTS,...",
    )
    product_warehouse_ids = fields.One2many(
        "product.stock.warehouse",
        "product_id",
        "Storage location",
        help="Configure storage location" " to each warehouse",
    )

    # TODO: Check if module lifecycle can be used here in v14.0
    state = fields.Selection(
        selection=[
            ("draft", "In Development"),
            ("sellable", "Normal"),
            ("end", "End of Lifecycle"),
            ("obsolete", "Obsolete"),
            ("temporary", "Temporary"),
            ("support", "Support"),
        ],
        help="State of lifecycle of the product.",
    )
    project_or_replacement = fields.Selection(
        selection=[
            ("project", "Project"),
            ("replacement", "Replacement"),
            ("projrepl", "Project Replacement"),
        ],
        help="The product is usually used for a new PROJECT, is used "
        "to REPLACE some component or is used for both.",
    )
    ref_ac = fields.Selection(
        selection=[
            ("ref", "Refrigeration"),
            ("ac", "AC"),
            ("refac", "Refrigeration AC"),
        ],
        string="Refrigeration/AC",
        help="The product is used for Refrigeration, Air Conditioning or both.",
    )
    final_market = fields.Selection(
        selection=[
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
    main_customer_activity = fields.Selection(
        selection=[
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
        selection=[
            ("nulo", "Nulo"),
            ("nday", "Next day"),
            ("nurg", "Not urgent"),
        ],
        help="The delivery time according to the priority and importance of "
        "the product is Null if it can not wait, Next Day if the time is "
        "moderate and No Urgent if we can wait to have it.",
    )
    type_of_client = fields.Selection(
        selection=[
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
        selection=[
            ("ns", "Insensitive"),
            ("ps", "Little sensitive"),
            ("n", "Neutral"),
            ("as", "Something sensitive"),
            ("ms", "Very sensitive"),
        ],
        help="Field to know how much the price of the product impacts the " "customers decision to purchase.",
    )
    product_nature = fields.Selection(
        selection=[
            ("commodity", "Commodity"),
            ("specialty", "Specialty"),
            ("normal", "Normal"),
        ],
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
    report_id = fields.Many2one("ir.actions.report", "Label report", domain="[('model','=','product.product')]")
    normalized_barcode = fields.Boolean(
        default=True,
        string="Normalized",
        help="The supplier will provide a "
        "proper barcode if True if not "
        "then you can generate your own "
        "barcode",
    )

    # TODO: It was spit_method in 11.0 then this need to be reviewed

    def generate_barcode(self, *args, **kw):
        self.ensure_one()
        if self.normalized_barcode:
            return True
        return super().generate_barcode(*args, **kw)
