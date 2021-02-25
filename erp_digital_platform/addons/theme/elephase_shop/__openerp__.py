{
    #Information
    'name': 'Elephase Shope',
    'category': 'website',
    'summary': "Elephase Request Process Pages",
    'version': '8.0.1',
    'author': 'Sheliya Infotech',
    'description': """
        Elephase Request Process Pages
        """,
    'depends': ['elephase_base','website_sale_product_in_stock'],
    'data': [ 
        'templates/assets.xml',
        'templates/shop.xml',
        'templates/product_detail.xml',
        'templates/breadcum_template.xml',
        'templates/cart.xml',
        'templates/website_sale_cart_preview.xml',
        'views/inherited_product_template_view.xml',
    ],
    'application': False,
}
