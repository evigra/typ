from odoo import tools
from odoo import models, fields
import odoo.addons.decimal_precision as dp


class StockAnalysis(models.Model):
    _inherit = "stock.analysis"

    state = fields.Selection(
        [
            ("sellable", "Normal"),
            ("end", "End of Lifecycle"),
            ("obsolete", "Obsolete"),
        ],
        "Status",
    )
    partner_id = fields.Many2one("res.partner", string="Partner", readonly=True)
    product_min_qty = fields.Float("Minimum Quantity", readonly=True)
    product_max_qty = fields.Float("Maximum Quantity", readonly=True)
    warehouse_id = fields.Many2one("stock.warehouse", readonly=True)
    importance = fields.Selection([("aa", "AA"), ("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")])
    standard_price = fields.Float(
        digits=dp.get_precision("Product price"), readonly=True, groups="typ_stock.res_group_standard_price"
    )
    balanced = fields.Boolean(readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, "stock_analysis")
        cr.execute(
            """CREATE or REPLACE VIEW stock_analysis AS (
            SELECT row_number() over (order by prod.id DESC) AS id,
                prod.id AS product_id,
                COALESCE(quant.qty, 0.0) AS qty,
                quant.package_id,
                quant.lot_id,
                pph.cost AS standard_price,
                orderpoint.product_min_qty,
                orderpoint.product_max_qty,
                orderpoint.importance,
                orderpoint.warehouse_id,
                template.state AS state,
                template.categ_id AS categ_id,
                supplier.name AS partner_id,
                CASE
                    WHEN orderpoint.id IS NULL THEN (FALSE)
                    WHEN orderpoint.id IS NOT NULL THEN (TRUE)
                END AS balanced,
                CASE
                    WHEN quant.location_id IS NOT NULL
                        THEN (quant.location_id)
                    WHEN quant.location_id IS NULL
                    AND orderpoint.location_id IS NOT NULL
                        THEN(orderpoint.location_id)
                END AS location_id
            FROM
            (SELECT sq.product_id,
                    sq.location_id
            FROM stock_quant sq
            JOIN stock_location sl ON (sl.id=sq.location_id
                                        AND sl.usage='internal')
            GROUP BY sq.product_id,
                        sq.location_id
            UNION SELECT swo.product_id,
                            swo.location_id
            FROM stock_warehouse_orderpoint swo
            WHERE swo.active=TRUE ) sq
            LEFT JOIN
            (SELECT MIN(sq.id) AS id,
                    sq.product_id,
                    sq.location_id,
                    SUM(sq.qty) AS qty,
                    sq.package_id,
                    sq.lot_id
            FROM stock_quant sq
            GROUP BY sq.product_id,
                        sq.location_id,
                        sq.package_id,
                        sq.lot_id) quant ON quant.product_id=sq.product_id
            AND quant.location_id=sq.location_id
            FULL JOIN product_product prod ON prod.id=sq.product_id
            JOIN
            (SELECT id,
                    state,
                    categ_id
            FROM product_template
            WHERE TYPE='product'
                AND active=TRUE) TEMPLATE ON template.id = prod.product_tmpl_id
            LEFT JOIN
            (SELECT id,
                    product_id,
                    location_id,
                    product_min_qty,
                    product_max_qty,
                    importance,
                    warehouse_id
            FROM stock_warehouse_orderpoint
            WHERE active=TRUE) orderpoint
            ON orderpoint.product_id=sq.product_id
            AND orderpoint.location_id=sq.location_id
            LEFT JOIN
            (SELECT DISTINCT ON(product_tmpl_id) product_tmpl_id,
                            name
            FROM product_supplierinfo
            WHERE SEQUENCE=1
            GROUP BY product_tmpl_id,
                        name) supplier
                        ON supplier.product_tmpl_id = prod.product_tmpl_id
          JOIN
          (SELECT DISTINCT ON(product_template_id) product_template_id, cost
           FROM product_price_history
          ORDER BY product_template_id, datetime DESC
          ) pph ON pph.product_template_id=prod.product_tmpl_id
            )"""
        )
