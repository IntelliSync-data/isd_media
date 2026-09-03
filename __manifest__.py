{
    'name': 'Media Service (by ISD)',
    'version': '18.0.1.0.0',
    'category': 'ISD Modules',
    'summary': 'Centralized Media Service for ISD Platform',
    'description': """
        ISD Media Service
        =================
        Centralized media management service for the ISD Platform ecosystem.

        Features:
        - Image & Video management with Local Storage or Amazon S3
        - REST API for external systems (Portal, PhotoApp, Mobile App)
        - Category & Tag organization
        - Publish scheduling
        - Version API for cache optimization
        - Provider pattern for extensible storage backends
    """,
    'author': 'IntelliSync Data',
    'website': 'https://intellisyncdata.com',
    'license': 'LGPL-3',
    'depends': ['base', 'base_setup', 'bus'],
    'data': [
        # Security
        'security/isd_media_security.xml',
        'security/ir.model.access.csv',
        # Views
        'views/isd_media_views.xml',
        'views/isd_media_category_views.xml',
        'views/isd_media_tag_views.xml',
        'views/res_config_settings_views.xml',
        # Wizard
        'wizard/api_documentation_wizard_views.xml',
        # Menu
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
