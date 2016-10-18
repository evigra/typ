.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

=========
TYP Stock
=========

This module adding functionalities related with stock module.

**Allow propagate transfer pickings.**

This functionality allow transfer picking by propagation. To do this, it is
necessary check the field ``Propagate transfer`` in object procurement rule
related with stock move.

When the field ``Propagate transfer`` is check in all procurement rules related
with the stock moves created in a sale order, with make the transfer of first
picking, all other pickings it will be transfered automatically.

**Validation to warehouses to not allow negative availability in product.**

This functionality allows warehouses to prevent negative numbers. Limiting 
the warehouses not to allow movements generate if no stock.

**Validation for internal movements in locations scrapped.**

This functionality allows only users group manager/warehouse, confirm and 
validate movements locations losses or scraped.

**Validation for return of customers from sale order.**

This functionality validate quantity return for customers for the purpose not 
to exceed the quatities invoiced from the sales order.

**Adding Refactoring Reording Rules & wizard for Minimun Stock Supply**
inherit methods and base views related with supply orders & wizards Run
Schedulers & Compute stock Minimum Rules Only by the group "Users that can
run schedulers warehouse".

It allows you to select a specific store and supply without having to run 
the general supply.

The methods inherit original path is: 

Credits
=======

**Contributors**

* Julio Serna <julio@vauxoo.com> (Planner/Auditor)
* Yennifer Santiago <yennifer@vauxoo.com (Developer)
* Jorge Escalona <jorge@vauxoo.com> (Developer)
* Deivis Laya <deivis@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
    :alt: Vauxoo
    :target: https://www.vauxoo.com
    :width: 200

This module is maintained by Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
