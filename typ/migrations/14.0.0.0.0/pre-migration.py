import logging

from odoo import tools

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    use_native_hr_marital_cohabitant(cr)
    sanitize_employee_blood_types(cr)
    rename_field_so_is_special(cr)


def use_native_hr_marital_cohabitant(cr):
    """Use the native  marital status "Legal Cohabitant"

    That marital status didn' exist in 11.0, so we added a custom one. But
    it's now supported, thanks to:
    https://github.com/odoo/odoo/commit/0eb58775c9e9
    """
    _logger.info("Updating employee's marital status to use the native cohabitant")
    cr.execute(
        """
        UPDATE
            hr_employee
        SET
            marital = 'cohabitant'
        WHERE
            marital = 'cohabiting';
        """
    )
    _logger.info("Updated %d employees", cr.rowcount)


def sanitize_employee_blood_types(cr):
    """Fix blood types to fid posible selections

    Blood type was a char and now it's a selection, and there are a few cases that need sanitizing.
    """
    _logger.info("Sanitizing employee's blood types")
    allowed_types = (
        "A-",
        "A+",
        "B-",
        "B+",
        "AB-",
        "AB+",
        "O-",
        "O+",
    )
    cr.execute(
        """
        UPDATE
            hr_employee
        SET
            blood_type = CASE
                WHEN
                    blood_type like '%%RH%%'
                THEN
                    REPLACE(REPLACE(blood_type, 'RH', ''), ' ', '')
                ELSE
                    NULL
                END
        WHERE
            blood_type NOT IN %s;
        """,
        [allowed_types],
    )
    _logger.info("Updated %d employees", cr.rowcount)


def rename_field_so_is_special(cr):
    """Rname sale order field "so" -> "is_special"

    The field name "so" doesn't give any useful information and it's not allowed by lints.
    """
    if tools.column_exists(cr, "sale_order", "so"):
        _logger.info("Renaming sale order field `so` -> `is_special`")
        tools.rename_column(cr, "sale_order", "so", "is_special")
