
from .common import TestTypSaleTeam


class TestDefaultJournalLandedGuide(TestTypSaleTeam):

    def test_00_default_journal_landed_guide(self):
        """Test that Journal in Landed Guides is set depends Sale Team
        configuration.
        """
        self.sale_team.write({
            'default_warehouse': self.warehouse.id,
            'journal_guide_id': self.journal_landed_guide.id,
            'journal_landed_id': self.journal_landed.id, })
        self.guide_dict_vals.update(
            {'journal_id': self.journal_landed_guide.id})
        landed_guide = self.env['stock.landed.cost.guide'].create(
            self.guide_dict_vals)
        landed_guide.write({'warehouse_id': self.warehouse.id})
        landed_guide.onchange_warehouse_id()
        self.assertEqual(landed_guide.journal_id, self.journal_landed_guide)
