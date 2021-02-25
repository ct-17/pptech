# -*- coding: utf-8 -*-
# __author__ = 'BinhTT'
##############################################################################

{
    'name': 'DP Pricelist Website',
    'version': '1.1',
    'author': 'OpenERP SA',
    'category': 'Pricelist',
    'description': """
Module to manage the payment of your supplier invoices.
=======================================================

This module allows you to create and manage your pricelist, with purposes to
--------------------------------------------------------------------------------- 
    * control chandler pricelist

Warning:
~~~~~~~~
The confirmation of a payment order does _not_ create accounting entries, it just 
records the fact that you gave your payment order to your bank. The booking of 
your order must be encoded as usual through a bank statement. Indeed, it's only 
when you get the confirmation from your bank that your order has been accepted 
that you can book it in your accounting. To help you with that operation, you 
have a new option to import payment orders as bank statement lines.
    """,
    'depends': ['dp_base',
                'dp_website_sale_extend',
                'dp_website_myaccount',
                'dp_website_product_suggest'
                ],
    'data': [
        'templates.xml',
        'views/my_account.xml',
        'views/shop.xml',
    ],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
