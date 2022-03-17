import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    reenable_rules_traffic(cr)


def reenable_rules_traffic(cr):
    """Re-enable record rules related to the traffic group

    Those rules were manually deactivated in production because they were causing issues.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    group_traffic = env.ref("typ.group_traffic")
    rules = group_traffic.with_context(active_test=False).rule_groups
    assert len(rules) == 3, rules.mapped("name")
    rules.write({"active": True})
    _logger.info("The folowwing rules were re-enabled: %s", rules.mapped("name"))
