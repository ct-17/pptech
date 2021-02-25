{
    'name': 'Product Template Stock Level Indicator DigitalPlatform',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    This module help
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_common', 'stock', 'dp_product'],
    'data': [
        "templates.xml",
        "views/product_template.xml",
        "security/ir.model.access.csv",
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
