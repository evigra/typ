.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

===========
Typ Account
===========

This module adding the follow functionalities.

**Show credit limit message in sale order.**

- When a client with credit closed is selected in a sale order, a warning
  message is displayed to notify the client status to the user.

**Show credit limit message in invoicing.**

- When a client with credit closed is selected on an invoice, a warning
  message is displayed to notify the client status to the user.

**Invoice validation**

- The credit limit is only validated in invoices of type 'out_invoice'.
- The invoice validation date is stored in database

**Validates creation of policy for employees advance**

- The advance of employee are validate in creation of policy without tax.

Credits
=======

**Contributors**

* Julio Serna <julio@vauxoo.com> (Planner/Auditor)
* Yennifer Santiago <yennifer@vauxoo.com (Developer)
* Carlos Fernando Mexia <cmexia@typrefrigeracion.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
    :alt: Vauxoo
    :target: https://www.vauxoo.com
    :width: 200

This module is maintained by Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
