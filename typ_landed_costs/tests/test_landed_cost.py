# -*- coding: utf-8 -*-

from openerp.exceptions import ValidationError
from .common import TestTypLandedCosts


class TestLandedCost(TestTypLandedCosts):

    def test_00_only_valid_guides(self):
        """Check a landed cost only can use valid guides"""
        guide = self.create_guide()
        landed = self.create_landed()
        landed.write({'guide_ids': [(6, 0, guide.ids)]})
        msg = ".*Only valid guides can be added to a landed cost.*"
        with self.assertRaisesRegexp(ValidationError, msg):
            landed.button_validate()
