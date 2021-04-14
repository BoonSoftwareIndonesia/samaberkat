# -*- coding: utf-8 -*-
# from odoo import http


# class EndingBalance(http.Controller):
#     @http.route('/ending_balance/ending_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ending_balance/ending_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ending_balance.listing', {
#             'root': '/ending_balance/ending_balance',
#             'objects': http.request.env['ending_balance.ending_balance'].search([]),
#         })

#     @http.route('/ending_balance/ending_balance/objects/<model("ending_balance.ending_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ending_balance.object', {
#             'object': obj
#         })
