{
    'name': 'Mark Up Discount Sales DigitalPlatform',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    This module helps to integrate mark up and discount modules. 
    This overwrites base module for discount and mark up computation method 
    to add mark up value before apply discount
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_sale', 'dp_markup', 'np_discount'],
    'data': [
        'views/sale_order_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
