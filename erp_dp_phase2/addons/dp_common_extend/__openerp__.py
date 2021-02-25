{
    'name': 'Extend DP Common',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_common'],
    'data': [
        'views/shipmaster_invitaiton_list.xml',
        'views/web_admin_role.xml',
        "security/ir.model.access.csv",
        "views/replace_error_template.xml",
        "views/chandler_detail.xml",
        "views/chandler_shipmaster.xml",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
