.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================
Customer Invoice
=================

This module provides ``customer_invoice``, a standalone SSI transactional
document with its own table -- it does not reuse or extend the
``account.move`` table. The document follows the standard SSI workflow
(``draft`` -> ``confirm`` -> ``open``/``reject`` -> ``done``, plus
``cancel``) with multiple approval. When the document is confirmed and
approved into the ``open`` state, it generates its own ``account.move``
record (linked through the ``move_id`` field). The document then
transitions automatically to ``done`` once the receivable journal item on
that ``account.move`` is fully reconciled, and back to ``open`` if the
reconciliation is undone.


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/ssi-customer-invoice
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Customer Invoice*
6.  Install the module


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/ssi-customer-invoice/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
