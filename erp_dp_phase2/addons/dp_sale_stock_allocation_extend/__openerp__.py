{
    'name': 'Sales Stock Allocation DigitalPlatform - Extend',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    This module helps to track stock allocation when duplicating sale order upon sending order to more than 1 chandler. 
    """,
    'author': "Elephas ",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_sale'],
    'data': [
        'views/sale_line_stock_allocation.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
