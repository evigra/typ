import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    fix_currency_amls(cr)
    reenable_orphan_invoice_lines(cr)


def fix_currency_amls(cr):
    """Fix currency on journal items that don't match currency set on journal entry"""
    cr.execute(
        """
        UPDATE
            account_move_line AS aml
        SET
            currency_id = am.currency_id
        FROM
            account_move AS am
        WHERE
            aml.move_id = am.id
            AND aml.currency_id != am.currency_id
            AND am.move_type IN ('in_invoice', 'in_refund');
        """
    )
    _logger.info("Currency was fixed on %d vendor bill lines", cr.rowcount)


def reenable_orphan_invoice_lines(cr):
    """Re enable invoice lines that were not fully migrated

    Some invoice lines were not fully migrated to journal items because, prior to migration, values of
    journal items didn't match the ones on invoice lines. So Odoo just created new journal items of type
    "Section" that are ignored.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute(
        """
        WITH invoice_line AS (
            SELECT
                aml.id,
                aml.product_id,
                aml.price_subtotal,
                aml.discount,
                aml.price_unit,
                aml.company_id,
                aml.move_id,
                split_part(property.value_reference, ',', 2)::INT AS categ_account_id
            FROM
                account_move_line AS aml
            INNER JOIN
                account_move AS am
                ON am.id = aml.move_id
            INNER JOIN
                product_product AS product
                ON aml.product_id = product.id
            INNER JOIN
                product_template AS ptemplate
                ON product.product_tmpl_id = ptemplate.id
            INNER JOIN
                product_category AS categ
                ON ptemplate.categ_id = categ.id
            INNER JOIN
                ir_property AS property
                ON property.res_id = CONCAT('product.category,', categ.id)
                AND property.company_id = aml.company_id
            WHERE
                aml.display_type IS NOT NULL
                AND aml.price_unit IS NOT NULL
                AND aml.product_id IS NOT NULL
                AND am.move_type IN ('in_invoice', 'in_refund')
                AND property.name = 'property_stock_account_input_categ_id'
        )
        UPDATE
            account_move_line AS aml
        SET
            exclude_from_invoice_tab = FALSE,
            price_unit = inv_line.price_unit,
            price_subtotal = inv_line.price_subtotal
        FROM
            invoice_line AS inv_line
        WHERE
            aml.product_id = inv_line.product_id
            AND aml.move_id = inv_line.move_id
            AND aml.account_id = inv_line.categ_account_id
        RETURNING aml.move_id
        """
    )
    _logger.info("Amounts were fixed on %d invoice lines", cr.rowcount)

    # Recompute amounts on invoices whose lines have changed
    invoice_ids = {r[0] for r in cr.fetchall()}
    invoices = env["account.move"].browse(invoice_ids)
    invoices._compute_amount()
    _logger.info("Invoice amounts were recomputed on %d records", len(invoices))
