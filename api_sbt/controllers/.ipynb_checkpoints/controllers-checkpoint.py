# -*- coding: utf-8 -*-
import json, datetime, base64
from odoo import http
from odoo.http import request, Response
from datetime import datetime


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

    def getRecord(self, model, field, oms):
        record = request.env[model].search([(field,'=',oms)])
        if record[field] == oms:
            return record['id']
        else:
            return -1
    
    @http.route('/api/authenticate', type='json', auth='none', methods=['POST'])
    def authenticate(self, db, login, password):
        try:
            request.session.authenticate(db, login, password)
            return request.env['ir.http'].session_info()
        except:
#            Response.status = "401"
            return {"Error": "Failed to authenticate user"}

    @http.route('/api/createap', type='json', auth='user', methods=['POST'])
    def post_ap(self, ap):
        created = 0
        error = {}
        warn_cnt = 1
        bill_lines = []
        temp_vendor = 0
        is_error = False
        response_msg = "Failed to create bill!"
        message = {}
        
        #Create log
        try:
            api_log = request.env['api_sbt.api_sbt'].create({
                'status': 'new',
                'created_date': datetime.now(),
                'incoming_msg': ap,
                'message_type': 'ap'
            })

            api_log['status'] = 'process'
        except:
            error['Error'] = str(e)
            is_error = True
        
        try:
            api_log['incoming_txt'] = request.env['ir.attachment'].create({
                'name': str(api_log['name']) + '_in.txt',
                'type': 'binary',
                'datas': base64.b64encode(bytes(str(ap), 'utf-8')),
                'res_model': 'api_sbt.api_sbt',
                'res_id': api_log['id'],
                'mimetype': 'text/plain'
            })
        except Exception as e:
            error['Error'] = str(e)
            is_error = True
        
        try:
            for rec in ap:
                temp_state = 0
                temp_country = 0
                temp_term = 0

                #Check omsPaymentNo
                bill = request.env['account.move'].search([('x_payment_no', '=', rec['omsPaymentNo']),('move_type', '=', 'in_invoice'),('state', '!=', 'cancel')])
                if bill['x_payment_no'] == rec['omsPaymentNo'] and bill['state'] == 'posted':
                    error["Error"] = "Document " + rec['omsPaymentNo'] + " has been posted"
                    is_error = True
                    break

                #Vendor
                if rec['subconCode'] == "":
                    error["Error"] = "Field subconCode is blank"
                    is_error = True
                    break

                temp_vendor = self.getRecord(model="res.partner", field="x_studio_subcon_code", oms=rec['subconCode'])
                if temp_vendor == -1:
                    #Check if subconName is blank
                    if rec['subconName'] == "":
                        error["Error"] = "Field subconName is blank"
                        is_error = True
                        break

                    #State
                    oms_state = str(rec['subconStateName']).title()
                    temp_state = self.getRecord(model="res.country.state", field="name", oms=oms_state)
                    if temp_state == -1:
                        error["Error"] = "State " + rec['subconStateName'] + " does not exist"
                        is_error = True
                        break

                    #Country
                    oms_country = str(rec['subconCountry']).title()
                    temp_country = self.getRecord(model="res.country", field="name", oms=oms_country)
                    if temp_country == -1:
                        error["Error"] = "Country " + rec['subconCountry'] + " does not exist"
                        is_error = True
                        break

                    #Payment Term
                    temp_term = self.getRecord(model="account.payment.term", field="x_studio_oms_term_code", oms=rec['subconPaymentTerm'])
                    if temp_term == -1:
                        error["Error"] = "Payment Term  " + rec['subconPaymentTerm'] + " does not exist"
                        is_error = True
                        break

                    created_vendor = request.env['res.partner'].create({
                        "x_studio_subcon_code": rec['subconCode'],
                        "name": rec['subconName'],
                        "street": rec['subconAddress'],
                        "city": rec['subconCity'],
                        "state_id": temp_state,
                        "zip": rec['subconZipCode'],
                        "country_id": temp_country,
                        "mobile": rec['subconMobileNo'],
                        "email": rec['subconEmail'],
                        "property_supplier_payment_term_id": temp_term,
                        "is_company": 'TRUE',
                        "supplier_rank": 1,
                        "property_account_receivable_id": 558,
                        "property_account_payable_id": 606,
                        "x_studio_account_number": rec['subconRemarks']
                    })

                    warn_str = "Message " + str(warn_cnt)
                    error[warn_str] = "Vendor " + rec['subconCode'] + " has been created"
                    warn_cnt += 1

                    temp_vendor = created_vendor['id']

                if is_error == True:
#                    Response.status = "400"
                    break

                #Bill Line
                for line in rec['apLine']:
                    temp_product = 0
                    temp_account = 0
                    temp_tax = []
                    
                    #G/L Account
                    if line['glCode'] == "":
                        error["Error"] = "Field glCode is blank"
                        is_error = True
                        break

                    temp_account = self.getRecord(model="account.account", field="code", oms=line['glCode'])
                    if temp_account == -1:
                        error["Error"] = "Account " + line['glCode'] + " does not exist"
                        is_error = True
                        break

                    #product
                    if line['paymentChargeCode'] == "":
                        error["Error"] = "Field paymentChargeCode is blank"
                        is_error = True
                        break

                    temp_product = self.getRecord(model="product.product", field="default_code", oms=line['paymentChargeCode'])
                    if temp_product == -1:
                        #Check paymentChargeCodeDesc
                        if line['paymentChargeCodeDesc'] == "":
                            error["Error"] = "Field paymentChargeCodeDesc is blank"
                            is_error = True
                            break

                        created_product = request.env['product.product'].create({
                            "default_code": line['paymentChargeCode'],
                            "name": line['paymentChargeCodeDesc'],
                            "property_account_income_id": temp_account,
                            "property_account_expense_id": temp_account
                        })

                        temp_product = created_product['id']

                        warn_str = "Message " + str(warn_cnt)
                        error[warn_str] = "Product " + line['paymentChargeCode'] + " has been created"
                        warn_cnt += 1

                    #Tax
                    tx = float(line['paymentTaxRate'])
                    tax = request.env['account.tax'].search([('amount', '=', tx),('type_tax_use', '=', 'purchase')])
                    if tax['amount'] == tx:
                        temp_tax.append(tax['id'])
                    else:
                        error["Error"] = "Tax " + line['paymentTaxRate'] + " does not exist"
                        is_error = True
                        break

                    #Check paymentQty
                    if line['paymentQty'] == "":
                        error["Error"] = "Field paymentQty is blank"
                        is_error = True
                        break

                    #Check paymentRate
                    if line['paymentRate'] == "":
                        error["Error"] = "Field paymentRate is blank"
                        is_error = True
                        break

                    if line['omsOrderDate'] == "":
                        order_date = ""
                    else:
                        try:
                            order_date = datetime.strptime(line['omsOrderDate'], '%d/%m/%Y').date()
                        except ValueError:
                            error["Error"] = "Wrong date format on omsOrderDate"
                            is_error = True
                            break

                    bill_line = {}
                    bill_line['x_line_number'] = line['payLineNo']
                    bill_line['product_id'] = temp_product
                    bill_line['account_id'] = temp_account
                    bill_line['quantity'] = line['paymentQty']
                    bill_line['price_unit'] = line['paymentRate']
                    bill_line['tax_ids'] = temp_tax
                    bill_line['x_remarks'] = line['paymentRemarks']
                    bill_line['x_no_ot'] = line['omsReference']
                    bill_line['x_destination'] = line['uocCode']
                    bill_line['x_order_no'] = line['omsOrderNo']
                    bill_line['x_order_date'] = order_date
                    bill_line['x_driver_first_name'] = line['driverFirstName']
                    bill_line['x_vehicle_number'] = line['vehicleId']

                    bill_lines.append(bill_line)

                if is_error == True:
#                    Response.status = "400"
                    break

                if rec["omsPaymentDate"] == "":
                    payment_date = ""
                else:
                    try:
                        payment_date = datetime.strptime(rec["omsPaymentDate"], '%d/%m/%Y').date()
                    except ValueError:
                        error["Error"] = "Wrong date format on omsPaymentDate"
                        is_error = True
                        break

                if rec["omsPayOpdate1"] == "":
                    invoice_date = ""
                else:
                    try:
                        invoice_date = datetime.strptime(rec["omsPayOpdate1"], '%d/%m/%Y').date()
                    except ValueError:
                        error["Error"] = "Wrong date format on omsPayOpdate1"
                        is_error = True
                        break

                if rec["omsPayOpdate2"] == "":
                    bill_date = ""
                else:
                    try:
                        bill_date = datetime.strptime(rec["omsPayOpdate2"], '%d/%m/%Y').date()
                    except ValueError:
                        error["Error"] = "Wrong date format on omsPayOpdate2"
                        is_error = True
                        break

                if rec["dueDate"] == "":
                    due_date = ""
                else:
                    try:
                        due_date = datetime.strptime(rec["dueDate"], '%d/%m/%Y').date()
                    except ValueError:
                        error["Error"] = "Wrong date format on dueDate"
                        is_error = True
                        break

                #If previous record exist, delete it first before creating the new record
                if bill['x_payment_no'] == rec['omsPaymentNo'] and bill['state'] == 'draft':
                    bill.unlink()

                result = request.env['account.move'].create({
                    "move_type": "in_invoice",
                    "journal_id": 2,
                    "x_payment_no": rec['omsPaymentNo'],
                    "partner_id": temp_vendor,
                    "x_payment_date": payment_date,
                    "date": invoice_date,
                    "invoice_date": bill_date,
                    "invoice_date_due": due_date,
                    "invoice_line_ids": bill_lines,
                    "x_oms_ref": rec['apLine'][0]['omsReference']
                })
                created += 1

                response_msg = "Bill created successfully, ID: " + str(result['id'])
        except Exception as e:
            error["Error"] = str(e)
            is_error = True

        if is_error == True:
#            Response.status = "400"
            api_log['status'] = 'error'
        else:
            Response.status = "200"
            api_log['status'] = 'success'
        
        message = {
            'response': response_msg, 
            'message': error
        }
        
        api_log['response_msg'] = message
        api_log['response_date'] = datetime.now()
        
        api_log['response_txt'] = request.env['ir.attachment'].create({
            'name': str(api_log['name']) + '_out.txt',
            'type': 'binary',
            'datas': base64.b64encode(bytes(str(message), 'utf-8')),
            'res_model': 'api_sbt.api_sbt',
            'res_id': api_log['id'],
            'mimetype': 'text/plain'
        })
        
        return message

    @http.route('/api/createar', type='json', auth='user', methods=['POST'])
    def post_ar(self, ar):
        created = 0
        error = {}
        warn_cnt = 1
        inv_lines = []
        temp_cust = 0
        is_error = False
        response_msg = "Failed to create invoice!"
        
        #Create log
        try:
            api_log = request.env['api_sbt.api_sbt'].create({
                'status': 'new',
                'created_date': datetime.now(),
                'incoming_msg': ar,
                'message_type': 'ar'
            })

            api_log['status'] = 'process'
        except:
            error['Error'] = str(e)
            is_error = True
        
        try:
            api_log['incoming_txt'] = request.env['ir.attachment'].create({
                'name': str(api_log['name']) + '_in.txt',
                'type': 'binary',
                'datas': base64.b64encode(bytes(str(ar), 'utf-8')),
                'res_model': 'api_sbt.api_sbt',
                'res_id': api_log['id'],
                'mimetype': 'text/plain'
            })
        except Exception as e:
            error['Error'] = str(e)
            is_error = True
        
        try:
            for rec in ar:
                temp_state = 0
                temp_country = 0

                #Check invoiceNo
                inv = request.env['account.move'].search([('x_oms_invoice_no', '=', rec['invoiceNo']),('move_type', '=', 'out_invoice'),('state', '!=', 'cancel')])
                if inv['x_oms_invoice_no'] == rec['invoiceNo'] and inv['state'] == 'posted':
                    error["Error"] = "Document " + rec['invoiceNo'] + " has been posted"
                    is_error = True
                    break

                #Customer
                if rec['ownerCode'] == "":
                    error["Error"] = "Field ownerCode is blank"
                    is_error = True
                    break

                temp_cust = self.getRecord(model="res.partner", field="x_studio_owner_code", oms=rec['ownerCode'])
                if temp_cust == -1:
                    #Check ownerName
                    if rec['ownerName'] == "":
                        error["Error"] = "Field ownerName is blank"
                        is_error = True
                        break

                    #State
                    oms_state = str(rec['ownerStateName']).title()
                    temp_state = self.getRecord(model="res.country.state", field="name", oms=oms_state)
                    if temp_state == -1:
                        error["Error"] = "State " + rec['ownerStateName'] + " does not exist"
                        is_error = True
                        break

                    #Country
                    oms_country = str(rec['ownerCountry']).title()
                    temp_country = self.getRecord(model="res.country", field="name", oms=oms_country)
                    if temp_country == -1:
                        error["Error"] = "Country " + rec['ownerCountry'] + " does not exist"
                        is_error = True
                        break

                    #Payment Term
                    temp_term = self.getRecord(model="account.payment.term", field="x_studio_oms_term_code", oms=rec['ownerTermCode'])
                    if temp_term == -1:
                        error["Error"] = "Payment Term  " + rec['ownerTermCode'] + " does not exist"
                        is_error = True
                        break

                    created_cust = request.env['res.partner'].create({
                        "x_studio_owner_code": rec['ownerCode'],
                        "name": rec['ownerName'],
                        "street": rec['ownerAddress1'],
                        "city": rec['ownerCity'],
                        "state_id": temp_state,
                        "zip": rec['ownerZipCode'],
                        "country_id": temp_country,
                        "mobile": rec['ownerMobileNo1'],
                        "email": rec['ownerEmail1'],
                        "property_payment_term_id": temp_term,
                        "is_company": 'TRUE',
                        "customer_rank": 1,
                        "property_account_receivable_id": 558,
                        "property_account_payable_id": 606
                    })

                    warn_str = "Message " + str(warn_cnt)
                    error[warn_str] = "Customer " + rec['ownerCode'] + " has been created"
                    warn_cnt += 1

                    temp_cust = created_cust['id']

                if is_error == True:
#                    Response.status = "400"
                    break

                for line in rec['arLine']:
                    temp_product = 0
                    temp_account = 0
                    temp_tax = []
                    
                    #G/L Account
                    if line['glCode'] == "":
                        error["Error"] = "Field glCode is blank"
                        is_error = True
                        break

                    temp_account = self.getRecord(model="account.account", field="code", oms=line['glCode'])
                    if temp_account == -1:
                        error["Error"] = "Account " + line['glCode'] + " does not exist"
                        is_error = True
                        break

                    #product
                    if line['billingChargeCode'] == "":
                        error["Error"] = "Field billingChargeCode is blank"
                        is_error = True
                        break

                    temp_product = self.getRecord(model="product.product", field="default_code", oms=line['billingChargeCode'])
                    if temp_product == -1:
                        #Check billingChargeCodeDesc
                        if line['billingChargeCodeDesc'] == "":
                            error["Error"] = "Field billingChargeCodeDesc is blank"
                            is_error = True
                            break

                        created_product = request.env['product.product'].create({
                            "default_code": line['billingChargeCode'],
                            "name": line['billingChargeCodeDesc'],
                            "property_account_income_id": temp_account,
                            "property_account_expense_id": temp_account
                        })

                        temp_product = created_product['id']

                        warn_str = "Message " + str(warn_cnt)
                        error[warn_str] = "Product " + line['billingChargeCode'] + " has been created"
                        warn_cnt += 1                    

                    #Tax
                    tx = float(line['billingTaxRate'])
                    tax = request.env['account.tax'].search([('amount', '=', tx),('type_tax_use', '=', 'sale')])
                    if tax['amount'] == tx:
                        temp_tax.append(tax['id'])
                    else:
                        error["Error"] = "Tax " + line['billingTaxRate'] + " does not exist"
                        is_error = True
                        break

                    #Check billingQty
                    if line['billingQty'] == "":
                        error["Error"] = "Field billingQty is blank"
                        is_error = True
                        break

                    #Check billingRate
                    if line['billingRate'] == "":
                        error["Error"] = "Field billingRate is blank"
                        is_error = True
                        break

                    if line['omsOrderDate'] == "":
                        order_date = ""
                    else:
                        try:
                            order_date = datetime.strptime(line['omsOrderDate'], '%d/%m/%Y').date()
                        except ValueError:
                            error["Error"] = "Wrong date format on omsOrderDate"
                            is_error = True
                            break

                    inv_line = {}
                    inv_line['x_line_number'] = line['invLineNo']
                    inv_line['product_id'] = temp_product
                    inv_line['account_id'] = temp_account
                    inv_line['quantity'] = line['billingQty']
                    inv_line['price_unit'] = line['billingRate']
                    inv_line['tax_ids'] = temp_tax
                    inv_line['x_remarks'] = line['billingRemarks']
                    inv_line['x_no_ot'] = line['omsReference']
                    inv_line['x_destination'] = line['uocCode']
                    inv_line['x_order_no'] = line['omsOrderNo']
                    inv_line['x_order_date'] = order_date
                    inv_line['x_driver_first_name'] = line['driverFirstName']
                    inv_line['x_vehicle_number'] = line['vehicleId']

                    inv_lines.append(inv_line)

                if is_error == True:
#                    Response.status = "400"
                    break

                if rec["invoiceDate"] == "":
                    invoice_date = ""
                else:
                    try:
                        invoice_date = datetime.strptime(rec["invoiceDate"], '%d/%m/%Y').date()
                    except ValueError:
                        error["Error"] = "Wrong date format on invoiceDate"
                        is_error = True
                        break

                if rec["dueDate"] == "":
                    due_date = ""
                else:
                    try:
                        due_date = datetime.strptime(rec["dueDate"], '%d/%m/%Y').date()
                    except ValueError:
                        error["Error"] = "Wrong date format on dueDate"
                        is_error = True
                        break

                #If previous record exist, delete it first before creating the new record
                if inv['x_oms_invoice_no'] == rec['invoiceNo'] and inv['state'] == 'draft':
                    inv.unlink()

                result = request.env['account.move'].create({
                    "move_type": "out_invoice",
                    "journal_id": 1,
                    "x_oms_invoice_no": rec['invoiceNo'],
                    "partner_id": temp_cust,
                    "invoice_date": invoice_date,
                    "invoice_date_due": due_date,
                    "invoice_line_ids": inv_lines
                })
                created += 1

                response_msg = "Invoice created successfully, ID: " + str(result['id'])
                
        except Exception as e:
            error["Error"] = str(e)
            is_error = True

        if is_error == True:
#            Response.status = "400"
            api_log['status'] = 'error'
        else:
            Response.status = "200"
            api_log['status'] = 'success'
            
        message = {
            'response': response_msg, 
            'message': error
        }
        
        api_log['response_msg'] = message
        api_log['response_date'] = datetime.now()
        
        api_log['response_txt'] = request.env['ir.attachment'].create({
            'name': str(api_log['name']) + '_out.txt',
            'type': 'binary',
            'datas': base64.b64encode(bytes(str(message), 'utf-8')),
            'res_model': 'api_sbt.api_sbt',
            'res_id': api_log['id'],
            'mimetype': 'text/plain'
        })
        
        return message
