from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    uninstall_deprecated_modules(cr)


def uninstall_deprecated_modules(cr):
    """Remove all modules related to maintenance and quality

    Those modules are not being used anyway and we don't want overcharges.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    modules_to_uninstall = (
        "hr_maintenance",
        "maintenance",
        "mrp_maintenance",
        "mrp_workorder",
        "purchase_mrp_workorder_quality",
        "quality",
        "quality_control",
        "quality_mrp",
        "quality_mrp_workorder",
        "stock_barcode_quality_control",
    )
    modules = env["ir.module.module"].search([("name", "in", modules_to_uninstall)])

    # Ensure no module depends on the modules because they would be also uninstalled
    downstream_dependencies = modules.downstream_dependencies()
    assert not downstream_dependencies, downstream_dependencies.mapped("name")
    modules.button_uninstall()
