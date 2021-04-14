# -*- coding: utf-8 -*-
{
    'name': "Automate Ending Balance",

    'summary': "Custom function to automate ending balance on bank and cash statements",

    'description': "Custom function to automate ending balance on bank and cash statements",

    'author': "Boon Software",
    'website': "http://www.boonsoftware.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
