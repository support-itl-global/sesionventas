# -*- coding: utf-8 -*-
{
    'name': "Sesion ventas",

    'summary': """Sesion venas""",

    'description': """
        Sesion para ventas
    """,

    'author': "aquíH",
    'website': "http://www.aquih.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['account','sale'],

    'data': [
        'views/sesion_ventas_view.xml',
        'views/sale_views.xml',
        'views/account_move_views.xml',
        'views/account_payment_view.xml',
        'views/account_journal_views.xml',
        'views/report_cierre_caja.xml',
        'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
        'views/report.xml'
    ],
}
