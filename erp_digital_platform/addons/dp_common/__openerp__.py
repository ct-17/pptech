{
    'name': 'Base DigitalPlatform',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    This module helps to use marketplace base feature. 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['base', 'email_template', 'stock', 'sale', 'account', 'website_mail',
                'product', 'sale_stock', 'purchase', 'website_sale', 'payment'],
    'data': [
        "security/dp_base_security.xml",
        "security/warehouse.xml",
        "security/chandler_user.xml",
        "security/chandler_admin.xml",
        "security/record_rules.xml",
        "views/currency_rate.xml",
        "views/hide_email_templates.xml",
        "views/shipmaster_invitation_view.xml",
        "security/ir.model.access.csv",
        "views/template_users.xml",
        ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
