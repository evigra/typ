from odoo import fields, models


class ResPartnerWarehouse(models.Model):
    _name = "res.partner.warehouse"
    _description = "Partner Warehouse Configuration"
    _order = "credit_limit desc"

    warehouse_id = fields.Many2one("stock.warehouse", required=True)
    user_id = fields.Many2one("res.users", string="Salesperson")
    credit_limit = fields.Float()
    allow_overdue_invoice = fields.Boolean("Allow overdue invoices")
    partner_id = fields.Many2one("res.partner", required=True, ondelete="cascade")

    _sql_constraints = [
        (
            "partner_warehouse_unic",
            "unique(partner_id, warehouse_id)",
            "Warehouse configuration must be unique per warehouse and partner.",
        ),
    ]
