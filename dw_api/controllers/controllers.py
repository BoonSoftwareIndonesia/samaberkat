# -*- coding: utf-8 -*-
from odoo import models, fields, api, http
from odoo.http import request
import json, datetime, requests


class DwApi(http.Controller):
    @http.route('/dw_api/dw_api/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    
    
#     @http.route('/dw_api/dw_api/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dw_api.listing', {
#             'root': '/dw_api/dw_api',
#             'objects': http.request.env['dw_api.dw_api'].search([]),
#         })

#     @http.route('/dw_api/dw_api/objects/<model("dw_api.dw_api"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dw_api.object', {
#             'object': obj
#         })
