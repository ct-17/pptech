{
    'name': 'Extend DP Purchase Template Extend',
    'summary': '',
    'version': '1.0',
    'category': 'DigitalPlatform',
    'description': """
    """,
    'author': "Elephas",
    'website': 'http://www.elephas.vn/',
    'depends': ['report', 'dp_purchase_template'],
    'data': [
        'report_template/report_template.xml',
        'report_template/np_purchase_order_header_footer_template.xml',
        'report_template/np_purchase_order_body_template.xml',
        'report_template/page formatting.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
