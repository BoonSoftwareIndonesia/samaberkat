# -*- coding: utf-8 -*-
import json, datetime
from odoo import http
from odoo.http import request, Response


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

    @http.route('/api/createap', type='json', auth='none', methods=['POST'])
    def post_ap(self, db, login, password, ap):
        #Authenticate Session
        request.session.authenticate(db, login, password)
        
        created = 0
        error = {}
        warn_cnt = 1
        bill_lines = []
        temp_vendor = 0
        is_error = False
        response_msg = ""
        
        for rec in ap:
            temp_state = 0
            
            #Vendor
            partner = request.env['res.partner'].search([('x_studio_subcon_code', '=', rec['subconCode'])])
            if partner['x_studio_subcon_code'] == rec['subconCode']:
                temp_vendor = partner['id']
            else:
                #State
                state = request.env['res.country.state'].search([('name', '=', rec['subconState'])])
                if state['name'] == rec['subconState']:
                    temp_state = state['id']
                else:
                    error["Error"] = "State  " + rec['subconState'] + " not found"
                    is_error = True
                    break
                
                created_vendor = request.env['res.partner'].create({
                    "x_studio_subcon_code": rec['subconCode'],
                    "name": rec['subconName'],
                    "street": rec['subconAddress'],
                    "city": rec['subconCity'],
                    "state_id": temp_state,
                    "zip": rec['subconZipCode'],
                    #"country_id": rec['subconCountry'],
                    "mobile": rec['subconMobileNo'],
                    "email": rec['subconEmail'],
                    #"property_supplier_payment_term_id": rec['subconPaymentTerm']
                    "is_company": 'TRUE',
                    "supplier_rank": 1,
                    "property_account_receivable_id": 558,
                    "property_account_payable_id": 606
                })
                
                warn_str = "Warning " + str(warn_cnt)
                error[warn_str] = "Vendor  " + rec['subconCode'] + " has been created"
                warn_cnt += 1
                
                temp_vendor = created_vendor['id']
            
            if is_error == True:
                break
            
            #Bill Line
            for line in rec['apLine']:
                temp_product = 0
                temp_account = 0
                temp_tax = []
                
                #product
                product = request.env['product.product'].search([('default_code', '=', line['paymentChargeCode'])])
                if product['default_code'] == line['paymentChargeCode']:
                    temp_product = product['id']
                else:
                    created_product = request.env['product.product'].create({
                        "default_code": line['paymentChargeCode'],
                        "name": line['paymentChargeCodeDesc'],
                        "property_account_income_id": line['glCode'],
                        "property_account_expense_id": line['glCode']
                    })
                    
                    temp_product = created_product['id']
                    
                    warn_str = "Warning " + str(warn_cnt)
                    error[warn_str] = "Product  " + line['paymentChargeCode'] + " has been created"
                    warn_cnt += 1
                
                #G/L Account
                account = request.env['account.account'].search([('code', '=', line['glCode'])])
                if account['code'] == line['glCode']:
                    temp_account = account['id']
                else:
                    error["Error"] = "Account  " + line['glCode'] + " not found"
                    is_error = True
                    break
                
                #Tax
                tx = float(line['paymentTaxRate'])
                tax = request.env['account.tax'].search([('amount', '=', tx),('type_tax_use', '=', 'purchase')])
                if tax['amount'] == tx:
                    temp_tax.append(tax['id'])
                else:
                    error["Error"] = "Tax  " + line['paymentTaxRate'] + " not found"
                    is_error = True
                    break
                
                order_date = datetime.datetime.strptime(line['omsOrderDate'], '%d/%m/%Y')
                
                bill_line = {}
                bill_line['product_id'] = temp_product
                bill_line['account_id'] = temp_account
                bill_line['quantity'] = line['paymentQty']
                bill_line['price_unit'] = line['paymentRate']
                bill_line['tax_ids'] = temp_tax
                bill_line['x_remarks'] = line['paymentRemarks']
                bill_line['x_no_ot'] = line['omsReference']
                bill_line['x_destination'] = line['uocCode']
                bill_line['x_payment_no'] = line['omsPaymentNo']
                bill_line['x_order_no'] = line['omsOrderNo']
                bill_line['x_order_date'] = order_date.date()
                bill_line['x_driver_first_name'] = line['driverFirstName']
                bill_line['x_vehicle_number'] = line['vehicleId']
                
                bill_lines.append(bill_line)
            
            if is_error == True:
                break
               
            payment_date = datetime.datetime.strptime(rec["omsPaymentDate"], '%d/%m/%Y')
            invoice_date = datetime.datetime.strptime(rec["omsPayOpdate1"], '%d/%m/%Y')
            bill_date = datetime.datetime.strptime(rec["omsPayOpdate2"], '%d/%m/%Y')
            due_date = datetime.datetime.strptime(rec["dueDate"], '%d/%m/%Y')
            
            result = request.env['account.move'].create({
                "move_type": "in_invoice",
                "journal_id": 2,
                "partner_id": temp_vendor,
                "x_payment_date": payment_date.date(),
                "date": invoice_date.date(),
                "invoice_date": bill_date.date(),
                "invoice_date_due": due_date.date(),
                "invoice_line_ids": bill_lines
            })
            created += 1
            
            response_msg = "Bill ID: " + str(result['id'])
        
        message = {
            'status': 200, 
            'response': response_msg, 
            'error': error, 
            'message': str(created) + ' record(s) created successfully'
        }
        return message