# -*- coding: utf-8 -*-

from .common import TestTypAccount


class TestBankStatement(TestTypAccount):

    def test_00_advance_employee(self):
        """Advance employee without tax
        """
        employee_user = self.env.ref('hr.employee_qdp')
        partner = self.env.ref('base.user_demo_res_partner')

        employee_user.write({'address_home_id': partner.id})

        account = partner.property_account_payable
        move_lines = self.create_statement(
            partner=partner, amount=-100, account_id=account)
        self.assertEquals(len(move_lines), 2, 'The policy has tax')
