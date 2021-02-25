{
    'name': 'Sales DigitalPlatform',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    This module helps to use marketplace sale feature. 
    """,
    'author': "Elephas ",
    'website': 'http://www.elephas.vn/',
    'depends': ['sale_margin', 'dp_common', 'stock_dropshipping', 'np_discount', 'web_readonly_bypass',
                'dp_base', 'dp_product'],
    'data': ["templates.xml",
             "views/email_templates.xml",
             "views/negotiation_wizard_view.xml",
             "views/sale_order_view.xml",
             "views/cron.xml",
             "views/ir_config_parameters.xml",
             "security/ir.model.access.csv"
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
