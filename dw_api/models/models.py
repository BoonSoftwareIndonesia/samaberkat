# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json, datetime, requests


class dw_api(models.Model):
    
    _inherit = "res.partner"
    
    @api.model
    def create(self, vals_list):
        url = "http://boonsoftwareindonesia-samaberkat-training-api-log-2905744.dev.odoo.com/api/partner"
        
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
            "Cookie": "session_id=b08e39e852188254e288b7f9e5ac111b6057ec9b",
            "Content-Type": "application/json",
            "Connection": "keep-alive"
        }
        
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        
        vals_list['street'] = str(r.text)
        
        partners = super(dw_api, self).create(vals_list)
        return partners
    
#     _name = 'dw_api.dw_api'
#     _description = 'dw_api.dw_api'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
