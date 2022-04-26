import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    init_field_financial_credit_limit(cr)


def init_field_financial_credit_limit(cr):
    """Initialize field "Financial Credit Limit" on partners, using the standard credit limit field"""
    cr.execute(
        """
        UPDATE
            res_partner
        SET
            financial_credit_limit = credit_limit
        WHERE
            credit_limit != 0;
        """
    )
    _logger.info("Financial credit limit was initialized on %d partners", cr.rowcount)
