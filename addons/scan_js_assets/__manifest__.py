{
    'name': "Scan JavaScript assets",

    'summary': """
        Just Newbie""",

    'description': """
        This module is a Scan JavaScript for Odoo 14.
    """,

    'author': "Rizky",
    'website': "http://www.wibicon.com",
    'price': 0.00,
    'currency': 'EUR',
    'category': 'Newbie',
    'version': '14.0.0.1',
    'license': 'Other proprietary',
    'depends': ['base', 'web'],
    'images': [
        # 'static/description/banner.jpg',
    ],

    'data': [
        'views/assets.xml',
        'views/views.xml'
    ],
    'application': True,
    # Loads the file hello_world.xml as QWeb and uses it to render the view.
    'qweb': [
        'static/src/xml/scan_js.xml',
    ],

}
