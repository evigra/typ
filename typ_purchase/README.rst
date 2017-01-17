.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

============
Typ Purchase
============

This module adding the follow functionalities.

**Tracking of purchase orders**

- Modify search request for quotation view and sales orders, adding the option 
  to search for "source document"
- Adding the create date of the purchase order to form and tree view
  to perform a better tracking of Purchases. also this date is on Readonly mode.
- Creating a search view to be able of group by state purchase orders
- Add shipment date to the Purchase order
- Add shipment date to the product in purchase order lines
- The Buyer in charge of the order is available in the order's form via buyer field
- Can handle shipment dates by order_line
- Purchase Orders can be group by Buyer

Usage
=====

* To set all order lines shipment dates at once, you must first add the products, then
  add the global order shipment date and automatically this module sets the values for you,
  also you can hande shipment dates per line simply adding it.

**Allow create purchase order separate with silimar characteristics**

- Always create a new Purchase Orders when is from a Sale Order.

Credits
=======

**Contributors**

* Julio Serna <julio@vauxoo.com> (Planner/Auditor)
* Deivis Laya <deivis@vauxoo.com (Developer)
* Carlos Mexia <cmexia@typrefrigeracion.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
    :alt: Vauxoo
    :target: https://www.vauxoo.com
    :width: 200

This module is maintained by Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
