{
    # Module information
    'name': 'Blue Backend Theme V8',
    'version': '1.0',
    'category': 'Themes/Backend',

    # Your information
    'license': 'AGPL-3',
    'summary': 'Blue Backend Theme V8',
    'images': [
        'images/screen.png'
    ],

    # Dependencies
    'depends': [
        'web',
    ],

    # Views templates, pages, menus, options and snippets
    'data': [
        'views/backend.xml',
    ],

    # Qweb templates
    'qweb': [
        'static/src/xml/backend.xml',
    ],

    # Technical options
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
