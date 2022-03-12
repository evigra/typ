import logging

from odoo import fields, tools

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    init_field_payment_journal(cr)


def init_field_payment_journal(cr):
    """Initialize journal entry's field "Payment Journal" by SQL for a faster update

    Journal item's related field is also initialized. Even though Odoo implements an optimization
    to initialize related fields using SQL, it's not triggered if the referenced field is computed,
    even if it's stored [1].

    [1] https://github.com/odoo/odoo/blob/328e858c1da6/odoo/fields.py#L818
    """
    # Initialize column on account_move
    _logger.info("Initializing column payment_journal_id on table account_move")
    tools.create_column(
        cr=cr,
        tablename="account_move",
        columnname="payment_journal_id",
        columntype=fields.Many2one.column_type[1],
        comment="Payment Journal",
    )
    cr.execute(
        """
        WITH paid_invoice AS (
            SELECT
                move.id AS move_id
            FROM
                account_move AS move
            WHERE
                move_type != 'entry'
                AND move.payment_state != 'not_paid'
        ),
        account_receivable_payable AS (
            SELECT
                account.id AS account_id
            FROM
                account_account AS account
            INNER JOIN
                account_account_type AS acc_type
                ON acc_type.id = account.user_type_id
            WHERE
                acc_type.type IN ('receivable', 'payable')
        ),
        journal_by_payment AS (
            SELECT
                aml.move_id AS invoice_id,
                MAX(
                    pay_move.journal_id
                    ORDER BY
                        pay_move.date DESC,
                        pay_move.name DESC,
                        pay_move.id DESC
                ) AS payment_journal_id
            FROM
                account_move_line AS aml
            INNER JOIN
                account_receivable_payable
                USING(account_id)
            INNER JOIN
                paid_invoice AS invoice
                USING (move_id)
            INNER JOIN
                account_partial_reconcile AS apr
                ON apr.debit_move_id = aml.id
                OR apr.credit_move_id = aml.id
            INNER JOIN
                account_move_line AS counterpart_aml
                ON counterpart_aml.id != aml.id
                AND (
                    apr.debit_move_id = counterpart_aml.id
                    OR apr.credit_move_id = counterpart_aml.id
                )
            INNER JOIN
                account_move AS pay_move
                ON pay_move.id = counterpart_aml.move_id
            GROUP BY
                invoice_id
        )
        UPDATE
            account_move AS invoice
        SET
            payment_journal_id = pay_journal.payment_journal_id
        FROM
            journal_by_payment AS pay_journal
        WHERE
            invoice.id = pay_journal.invoice_id;
        """
    )
    _logger.info("column has been set on %d rows", cr.rowcount)

    # Initialize column on account_move_line
    _logger.info("Initializing column payment_journal_id on table account_move_line")
    tools.create_column(
        cr=cr,
        tablename="account_move_line",
        columnname="payment_journal_id",
        columntype=fields.Many2one.column_type[1],
        comment="Payment Journal",
    )
    cr.execute(
        """
        UPDATE
            account_move_line AS aml
        SET
            payment_journal_id = move.payment_journal_id
        FROM
            account_move AS move
        WHERE
            aml.move_id = move.id
            AND move.payment_journal_id IS NOT NULL;
        """
    )
    _logger.info("column has been set on %d rows", cr.rowcount)
