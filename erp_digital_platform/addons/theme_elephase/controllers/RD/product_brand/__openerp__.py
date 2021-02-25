{
    'name': 'Product Brand Manager',
    'version': '8.0.0.1.0',
    'category': 'Product',
    'summary': 'Add brand to products',
    'author': 'Odoo',
    'license': 'AGPL-3',
    'depends': ['product'],
    'data': [
        'product_brand_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
