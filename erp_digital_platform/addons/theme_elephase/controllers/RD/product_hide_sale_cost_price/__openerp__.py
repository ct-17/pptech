# -*- coding: utf-8 -*-
{
    "name": "Hide Cost Price and Sale Price of product",
    "summary": "Hide product cost price and sale price",
    "description": """
        This module hide product sale price or cost price.
    """,
    "version": "8.0.1",
    "category": "Product",
    "depends": ['stock_account', 'product'],
    "data": [
        'security/product_security.xml',
        'views/product_template_views.xml',
        'views/product_views.xml',
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": True,
}
