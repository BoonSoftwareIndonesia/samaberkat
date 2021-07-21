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

class ApiController(models.Model):
    _inherit = "res.partner"
    
    @api.model
    def create(self, vals_list):
        last_req = request.env["dw_api.dw_api"].search([], limit=1, order="id desc")
        last_cookies = last_req['cookies'].split()[1]
        
        apiurl = "http://boonsoftwareindonesia-samaberkat-training-api-log-2905744.dev.odoo.com/api/partner"
        
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "partner": [
                    {
                        "name": "Nama Customer"
                    }
                ]
            }
        }
        
        headers = {
            "Cookie": last_cookies,
            "Content-Type": "application/json"
        }
        
        r = requests.post(apiurl, data=json.dumps(payload), headers=headers)
        
        vals_list['street'] = str(r.text)
        vals_list['city'] = str(last_cookies)
        
        partners = super(ApiController, self).create(vals_list)
        return partners