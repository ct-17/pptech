{
    'name': 'DP Product',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    This module helps to use marketplace Product feature. 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['product', 'website_sale'],
    'data': [
        'views/product_template.xml',
        'views/ir_cron.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
