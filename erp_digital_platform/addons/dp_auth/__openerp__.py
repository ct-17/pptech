{
    'name': 'Authentication/Invitation DigitalPlatform',
    'summary': '',
    'version': '1.1',
    'category': 'Website Customize',
    'description': """
    This module helps to use shipmaster signup/invitation marketplace feature. 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['auth_signup', 'website', 'dp_common'],
    'data': [
        "views/dp_auth_template.xml",
        "views/signup_template.xml",
        "views/res_partner_view.xml",
        "views/email_templates.xml",
        # "views/dp_base_menu_views.xml",
        "views/dp_chandler_confirm_template.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
