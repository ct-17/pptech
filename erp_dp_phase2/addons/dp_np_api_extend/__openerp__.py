{
    'name': 'API BUYTAXFREE-Newport ERP - Extend',
    'summary': '',
    'version': '1.1',
    'category': 'Website Customize',
    'description': """
    This module ensure BUYTAXFREE purchase order can create sale order in New Port ERP. 
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['dp_np_api'],
    'data': [
        'views/api_logs.xml',
        'views/cron.xml',
        'views/db_matrix_view.xml',
        'views/db_matrix_data.xml',
        'views/data.xml',
        'views/erp_data_sync.xml',
        'views/email_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
