{
    'name': 'Authentication/Invitation DigitalPlatform - Extend',
    'summary': '',
    'version': '1.1',
    'category': 'Website Customize',
    'description': """
    This module extends digital platform authorisation module. 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_auth'],
    'data': [
        "security/ir.model.access.csv",
        "view/template.xml",
        "view/signup_template.xml",
        "view/email_template.xml",
        "view/res_partner_view.xml",
        "wizard/new_user_attachment_guide.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
