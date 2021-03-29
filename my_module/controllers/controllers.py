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
    
    @http.route('/api/createpartner', type='json', auth='user', methods=['POST'])
    def post_partner(self, customer):
        
        for rec in customer:
            cust = request.env['res.partner'].create(rec)
        
        message = {'status': 200, 'response': cust, 'message': 'Succeed'}
        return message
    
    @http.route('/api/createbill', type='json', auth='user', methods=['POST'])
    def post_bill(self, bill):
        
        for rec in bill:
            result = request.env['account.move'].create(rec)
        
        message = {'status': 200, 'response': result, 'message': 'Succeed'}
        return message
    
    @http.route('/api/createbill2', type='json', auth='user', methods=['POST'])
    def post_bill_two(self, bill):
        products = request.env['product.product'].search([])
        partners = request.env['res.partner'].search([])
        temp_partner = 0
        
        for rec in bill:
            
            for line in rec["invoice_line_ids"]:
                for product in products:
                    if product["default_code"] == line["product_id"]:
                        line["product_id"] = product["id"]
            
            for partner in partners:
                if partner["name"] == rec["partner_id"]:
                    temp_partner = partner["id"]
                
            result = request.env['account.move'].create({
                "move_type": "in_invoice",
                "partner_id": temp_partner,
                "invoice_date": rec["invoice_date"],
                "date": rec["date"],
                "invoice_payment_term_id": rec["invoice_payment_term_id"],
                "journal_id": 2,
                "invoice_line_ids": rec["invoice_line_ids"]
            })
        
        message = {'status': 200, 'response': result, 'message': 'Succeed'}
        return message
