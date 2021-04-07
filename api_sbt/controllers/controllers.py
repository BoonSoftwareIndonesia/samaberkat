# -*- coding: utf-8 -*-
from odoo import http


class ApiSbt(http.Controller):
    @http.route('/api_sbt/api_sbt/', auth='public')
    def index(self, **kw):
        return "Hello, world"

#     @http.route('/api_sbt/api_sbt/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('api_sbt.listing', {
#             'root': '/api_sbt/api_sbt',
#             'objects': http.request.env['api_sbt.api_sbt'].search([]),
#         })

#     @http.route('/api_sbt/api_sbt/objects/<model("api_sbt.api_sbt"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('api_sbt.object', {
#             'object': obj
#         })

class BoonApiRequest(http.Controller):
    @http.route('/api/partner', type='json', auth='public', methods=['GET'])
    def get_partner(self, id):
        sales_rec = request.env['res.partner'].search([])
        sales = []
        for rec in sales_rec:
            vals = {
                'id': rec.id,
                'name': rec.name,
            }
            if rec.id == id:
                sales.append(vals)
        data = {'status': 200, 'response': sales, 'message': 'Succeed'}
        return data