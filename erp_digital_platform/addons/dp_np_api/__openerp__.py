{
    'name': 'API BUYTAXFREE-Newport ERP',
    'summary': '',
    'version': '1.1',
    'category': 'Website Customize',
    'description': """
    This module ensure BUYTAXFREE purchase order can create sale order in New Port ERP. 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_sale', 'dp_auth', 'dp_purchase', 'dp_product'],
    'data': [
        'views/api_logs.xml',
        'views/cron.xml',
        'views/res_partner.xml',
        "security/ir.model.access.csv",
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
