.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

===========
Typ Sale
===========

This module adding the follow functionalities.

**Able to order products from a different supplier to the assigned to the
product in special sale orders.**

- When a sale order is created with a sale order line that has a route with a
  procurement rule with buy action type, appears a field
  'Supplier for purchase' where is possible select a different supplier the
  product in sale order line has. This supplier is use to create the new
  purchase order.

**Table to configurate salesman and credit limit to each warehouse in
partner**

- With that functionality, when a partner or warehouse is selected in a sale
  order, the salesperson changed depending on the configuration realted.

**Margin on sale orders**
- Porcent (%) of Margin allowed to be modified on sale order

**Extends the functionality of customers in partner, adding new informative fields for tracking customers.**
General information about fields:

Importance: customer importance in company

- AA
- A
- B
- C
- NEW
- NEGOTIATION
- EMPLOYEE
- NOT CLASSIFIED

Potential customer : potential for getting new importance

- AA
- A
- B
- C
- NEW
- NEGOTIATION
- EMPLOYEE
- NOT CLASSIFIED

Business activity: type of partners

- CON - CONTRACTOR
- COM - COMPANY
- WHO - WHOLESALERS


Type of customer : more detailed type of customer

- OC - OPERATOR CONTRACTOR
- NC - NEW WORK CONTRACTOR
- PC - PROFESSIONAL CONTRACTOR
- RC - REFRIGERATION CONTRACTOR
- SP - SPECIFIER
- FSC - FOODSTUFF COMPANY
- SUP - SUPERMARKET COMPANY
- BOT - BOTTLER
- OTH - OTHERS
- WHC - WHOLESALER CONTRACTOR
- WW - WHOLESALER WHOLESALER
- WI - WHOLESALER IRONMONGER
- NOT CLASSIFIED

Dealer type

- PD - PREMIER DEALER
- AD - AUTHORIZED DEALER
- SD - SPORADIC DEALER

Region : Customer’s location

- NORTHWEST
- WEST
- CENTER
- NORTHEAST
- SOUTHEAST
- SOUTH

**Margin on sale orders**
- Porcent (%) of Margin allowed to be modified on sale order

Credits
=======

**Contributors**

* Julio Serna <julio@vauxoo.com> (Planner/Auditor)
* Yennifer Santiago <yennifer@vauxoo.com (Developer)
* Omar Mejia <omejia@typrefrigeracion.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
    :alt: Vauxoo
    :target: https://www.vauxoo.com
    :width: 200

This module is maintained by Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.

