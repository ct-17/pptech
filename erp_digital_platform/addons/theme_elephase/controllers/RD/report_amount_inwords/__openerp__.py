# -*- coding: utf-8 -*-
{
    'name': "Total Amount In Words",
    'support': 'support@optima.co.ke',

    'summary': """
        Display Total Amount in Words for Invoice, PO, Sales Order and Quote. Choose to also display in the PDF report of the same documents
        """,

    'description': """
        Display the Invoice Total, Sales Order Total, Quotation Total and Purchase Order Total in Words. Possible to show in 13 Different languages depending on the langauge of the partner/customer/supplier in Odoo 
    """,

    'author': "Optima ICT Services LTD",
    'website': "http://www.optima.co.ke",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '0.1',
    'price': 59,
    'currency': 'EUR',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/invoice_view.xml',
        'views/invoice.xml',
        'views/order_view.xml',
        'views/order.xml',
        'views/purchase_view.xml',
        'views/purchase.xml',
        'views/res_currency.xml',
        'data/res_currency_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'Application': True,
}
