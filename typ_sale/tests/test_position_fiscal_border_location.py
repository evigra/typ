from odoo.tests.common import TransactionCase


class TestFiscalPositionBorder(TransactionCase):

    def test_10_fiscal_position_customer_sale(self):
        """Validation of fiscal position assignment for clients with sales
        team in border location, with message if the partner has a fiscal
        position configured.
        """
        partner = self.env.ref('typ_sale.partner_01')
        product = self.env.ref('product.product_product_6')
        tax_model = self.env['account.tax']
        fiscal_position_model = self.env['account.fiscal.position']
        fiscal_position_tax_model = self.env['account.fiscal.position.tax']
        sales_team = self.env.ref('sales_team.crm_team_1')
        sale_order_model = self.env['sale.order']
        demo_user = self.env.ref('base.user_demo')

        tax_product_id = tax_model.create(
            dict(name="Include tax", amount='16.00',
                 type_tax_use='sale'))
        tax_border_id = tax_model.create(
            dict(name="Exclude tax", amount='8.00',
                 type_tax_use='sale'))

        fiscal_position_customer = fiscal_position_model.create(
            dict(name='Personas morales del régimen general',
                 l10n_mx_edi_code='Test 601'))

        fiscal_position_border = fiscal_position_model.create(
            dict(name='Sale 8%', l10n_mx_edi_code='Sale 8%'))

        fiscal_position_tax_model.create(
            dict(position_id=fiscal_position_border.id,
                 tax_src_id=tax_product_id.id,
                 tax_dest_id=tax_border_id.id))

        sales_team.write({'fiscal_position_id': fiscal_position_border.id})
        demo_user.write(
            {'sale_team_id': sales_team.id,
             'sale_team_ids': [(4, sales_team.id, None)]})

        dict_vals_sale = {
            'partner_id': partner.id,
            'partner_invoice_id': partner.id,
            'partner_shipping_id': partner.id,
            'order_line': [
                (0, 0,
                 {'name': product.name, 'product_id': product.id,
                  'product_uom_qty': 1, 'product_uom': product.uom_id.id,
                  'price_unit': 900, })], }

        sale_order = sale_order_model.sudo(demo_user).create(dict_vals_sale)
        sale_order.sudo(demo_user).onchange_partner_shipping_id()
        self.assertEqual(sale_order.fiscal_position_id, fiscal_position_border)

        # Partner configured with fiscal position
        partner.property_account_position_id = fiscal_position_customer
        with_fiscal = sale_order.sudo(demo_user).onchange_partner_shipping_id()
        self.assertIn('warning', with_fiscal.keys())
        self.assertEqual(sale_order.fiscal_position_id, fiscal_position_border)
