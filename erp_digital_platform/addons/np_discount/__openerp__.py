{
    'name': 'NP Discount',
    'summary': '',
    'version': '1.0',
    'category': 'Sale',
    'description': """
        GTS Discount,
        need create 1 product name is "Discount" and type = Service, 
        we will use product Discount to posting JE account for discount
        need to inherit np_sale and np_account bcz we have pro-forma invoice , 
        if don't have pro-forma invoice, just inherit sale and account module
    """,
    'author': "Elephas",
    'website': 'http://www.hanelsoft.vn/',

    'depends': ['stock_account', 'purchase', 'sale'],
    'data': ['wizard/sale_global_discount_wizard_view.xml',
             'views/account_invoice.xml',
             'views/sale_order_view.xml',
             'views/purchase_order_view.xml',
             'views/data.xml',
             'views/account_settings.xml',
             'security/ir.model.access.csv',
             'templates.xml',
             ],
    'js': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
