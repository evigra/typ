# coding: utf-8

from openerp import api, fields, models


class CrmCaseSection(models.Model):

    _inherit = "crm.team"

    journal_guide_id = fields.Many2one(
        'account.journal', 'Journal landed cost guide',
        help='It indicates journal to be used when landed cost guide is'
        ' created')
    journal_landed_id = fields.Many2one(
        'account.journal', 'Journal landed cost',
        help='It indicates journal to be used when landed cost is created')
    sale_pricelist_id = fields.Many2one(
        'product.pricelist', 'Default sale pricelist',
        help='It indicates the sale pricelist'
        ' to be used when partner is created')


class ProductPricelist(models.Model):

    _inherit = 'product.pricelist'

    partner_ids = fields.Many2many(
        'res.partner', 'pricelist_section_rel', 'partner_id', 'pricelist_id',
        string="Pricelist's partner",
        help="Choose the Pricelist that partner can see"
    )


class ResPartner(models.Model):

    _inherit = 'res.partner'

    @api.model
    def _get_sale_pricelist_id(self):
        sale_team = self.env.user.sale_team_id
        return sale_team and sale_team.sale_pricelist_id.id

    pricelist_ids = fields.Many2many(
        'product.pricelist', 'pricelist_section_rel', 'pricelist_id',
        'partner_id', string="Pricelist's partner",
        help="Choose the Pricelist that partner can see"
    )
    buyer_id = fields.Many2one(
        "res.users", "Buyer", sercheable=True
    )

    @api.multi
    def _compute_product_pricelist(self):
        """Overwrite _compute_product_pricelist method to set the pricelist
        for the new partner depending of the user's salesteam which is trying
        to create the partner.

        """
        product_pricelist = self._get_sale_pricelist_id() or None
        for rec in self:
            rec.property_product_pricelist = product_pricelist

    @api.multi
    @api.depends('user_ids.groups_id')
    def _compute_is_employee(self):
        for partner in self:
            partner_id = self.env['res.users'].search(
                [('partner_id', '=', partner.id),
                 ('share', '=', False)])
            if partner_id:
                partner.is_employee = partner_id.has_group('base.group_user')

    is_employee = fields.Boolean(
        compute='_compute_is_employee', string='Is Employee?',
        readonly=True, store=True,
        help="If user belongs to employee group return True",)
