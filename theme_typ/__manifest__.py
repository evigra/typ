{
    'name': 'Theme T&P',
    'summary': 'T&P Official Theme',
    'version': '11.0.0.0.0',
    'author': 'Vauxoo',
    'license': 'AGPL-3',
    'data': [
        'views/images_library.xml',
        'views/assets.xml',
        'views/layout.xml',

    ],
    'demo': [
        # 'demo/categories.xml',
    ],
    'category': 'Theme/Creative',
    'depends': [
        'website',
        'website_blog',
        'website_crm',
        'website_sale',
    ],
    'qweb': [
        'static/src/xml/portal.xml',
        'static/src/xml/rating.xml',
        'static/src/xml/templates.xml',
    ],
}
