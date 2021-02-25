{
    #Information
    'name': 'Elephase Website',
    'category': 'website',
    'summary': "Elephase Website",
    'version': '8.0.1',
    'author': 'Sheliya Infotech',
    'description': """
        This is the main module of Elephase Website
        """,
    'depends': ['website_sale_product_in_stock', 'website_favicon', 'website_logo', 'website_portal_sale', 'website_quick_addtocart', 'website_redirect_to_shop', 'website_sale_cart_preview', 'website_rate_product'],
    'data': [ 
        'templates/assets.xml',
        'templates/footer.xml',
        'templates/header.xml',
        'templates/homepage.xml',
        'templates/shop.xml',
        'templates/product_detail.xml',
        'templates/breadcum_template.xml',
        'templates/cart.xml',
        'templates/website_setting.xml',
        'templates/login.xml',
        'templates/signup.xml',
        'templates/reset_password.xml',
        
        'views/inherited_product_template_view.xml',
        
    ],
    'application': False,
}
