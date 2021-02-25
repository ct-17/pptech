# -*- coding: utf-8 -*-
{
    'name': 'Elephase Portal',
    'category': 'Website',
    'summary': 'Account Management Frontend for your Customers',
    'version': '8.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Sheliya Infotech',
    'website': 'https://www.odoo.com',
    'depends': [
        'elephase_base',
        'auth_signup',
        'website_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'templates/login.xml',
        'templates/signup.xml',
        'templates/reset_password.xml',
        'templates/website.xml',
        'templates/elephase_portal.xml',
        'templates/elephase_portal_sale.xml',
    ],
    'demo': [
        'demo/sale_order.xml',
    ],
    'installable': True,
}
