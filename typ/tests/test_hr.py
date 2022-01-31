from dateutil.relativedelta import relativedelta

from odoo.tests import tagged

from .common import TypTransactionCase


@tagged("hr")
class TestHr(TypTransactionCase):
    def test_01_employee_age(self):
        """Check employee's age is computed correctly"""
        # Employee will be 18 tomorrow
        birthday = self.today - relativedelta(years=18, days=-1)
        employee = self.create_employee(birthday=birthday)
        self.assertEqual(employee.age, 17)

        # If birthday is one day less, employee should be 18 today
        employee.birthday -= relativedelta(days=1)
        self.assertEqual(employee.age, 18)
