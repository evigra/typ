import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    unset_noupdate_typ_rules(cr)


def unset_noupdate_typ_rules(cr):
    """Unset noupdate on rules and groups so they may be easily updated by code"""
    cr.execute(
        """
        UPDATE
            ir_model_data
        SET
            noupdate = FALSE
        WHERE
            module = 'typ'
            AND model IN  ('ir.rule', 'res.groups')
            AND noupdate IS NOT FALSE;
        """
    )
    _logger.info("Noupdate was unset on %d record rules and groups", cr.rowcount)
