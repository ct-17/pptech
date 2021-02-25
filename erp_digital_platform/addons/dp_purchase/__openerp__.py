{
    'name': 'Purchase DigitalPlatform',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """ 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_common', 'purchase', 'email_template'],
    'data': ["views/email_templates.xml", "views/purchaser.xml",
             "views/so_id.xml"
             ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
