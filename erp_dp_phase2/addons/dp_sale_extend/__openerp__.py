{
    'name': 'Extend DP Sale',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_sale'],
    'data': [
        'views/email_templates.xml',
        'views/templates.xml',
		'views/sale_order_view.xml',
        'views/new_fields.xml',
        # 'security/ir.model.access.csv',
 		"views/B2C_backend_permission.xml",
 		"views/email_system_param.xml",
 		"views/sale_order_view_b2c.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
