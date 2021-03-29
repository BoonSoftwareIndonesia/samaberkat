# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response


class MyModule(http.Controller):
     @http.route('/api/test', auth='public', website="True")
     def index(self, **kw):
         return "Hello, world"

     @http.route('/my_module/my_module/objects/', auth='public')
     def list(self, **kw):
         return http.request.render('my_module.listing', {
             'root': '/my_module/my_module',
             'objects': http.request.env['my_module.my_module'].search([]),
         })
    
     @http.route('/my_module/my_module/objects/<model("my_module.my_module"):obj>/', auth='public')
     def object(self, obj, **kw):
         return http.request.render('my_module.object', {
             'object': obj
         })

class ExampleOdooRequest(http.Controller):
    @http.route('/api/list_event', type='json', auth='public', methods=['GET'])
    def get_list_event(self):
        return "Succeed"
