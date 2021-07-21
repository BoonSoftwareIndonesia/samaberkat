# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json, datetime, requests, datetime


class dw_api(models.Model):
    
    _name = 'dw_api.dw_api'
    _description = 'API Download'

    name = fields.Char()
    created_date = fields.Datetime(string="Created Date")
    cookies = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

    def api_authenticate(self):
        apiurl = "http://boonsoftwareindonesia-samaberkat-training-api-log-2905744.dev.odoo.com/api/authenticate"
        
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "db": "boonsoftwareindonesia-samaberkat-training-api-log-2905744",
                "login": "admin",
                "password": "admin"
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*"
        }
         
        r = requests.post(apiurl, data=json.dumps(payload), headers=headers)
        
        log = self.env['dw_api.dw_api'].create({
            "created_date": datetime.datetime.now(),
            "cookies": r.cookies
        })
