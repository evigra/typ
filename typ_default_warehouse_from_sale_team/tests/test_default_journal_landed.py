
from .common import TestTypSaleTeam


class TestDefaultJournalLanded(TestTypSaleTeam):

    def test_00_default_journal_landed(self):
        """Test that Journal in Landed is set depends default Sale Team user
        configuration.
        """
        self.sale_team.write({
            'default_warehouse': self.warehouse.id,
            'journal_guide_id': self.journal_landed_guide.id,
            'journal_landed_id': self.journal_landed.id, })
        self.user.write({
            'sale_team_ids': [(6, 0, [self.sale_team.id])],
            'sale_team_id': self.sale_team.id, })
        landed_cost = self.env['stock.landed.cost'].sudo(self.user).create(
            self.landed_dict_vals)
        self.assertEqual(landed_cost.account_journal_id,
                         self.journal_landed)
