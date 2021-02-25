{
    'name': 'Mark Up Sales DigitalPlatform',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    This module helps to calculate mark up values in sales order. 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_sale'],
    'data': [
            "views/global_markup_view.xml",
            "views/sale_order_view.xml"
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
