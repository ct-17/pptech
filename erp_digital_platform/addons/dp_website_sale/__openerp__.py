# -*- coding: utf-8 -*-
# License:  (http://elephas.vn)
{
    'name': 'DP WebSite Sales',
    'version': '8.0.0.0.1',
    'author': 'Elephas',
    'website': 'http://elephas.vn',
    'category': 'Website Customize',
    'depends': ['website_sale', 'dp_auth', 'dp_base'],
    'data': [
        'templates.xml',
        'views/shop.xml',
        'views/website_sale_flow.xml',
        'views/sale_order.xml',
        'views/product.xml',
        'views/product_detail.xml',
        'views/website_sale_cart_preview.xml',
        'security/ir.model.access.csv'
    ],
}
