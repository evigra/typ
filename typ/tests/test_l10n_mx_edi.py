from odoo.tests import tagged

from odoo.addons.l10n_mx_edi.tests import test_cfdi_xml


@tagged("l10n_mx_edi", "post_install", "-at_install")
class TestEdiResults(test_cfdi_xml.TestEdiResults):
    """This run native tests from l10n_mx_edi.

    There's no point on copying tests here. By inheriting the native class,
    native tests will be run.
    """
