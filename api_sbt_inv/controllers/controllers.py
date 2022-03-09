# -*- coding: utf-8 -*-
# from odoo import http


# class ApiSbtInv(http.Controller):
#     @http.route('/api_sbt_inv/api_sbt_inv/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/api_sbt_inv/api_sbt_inv/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('api_sbt_inv.listing', {
#             'root': '/api_sbt_inv/api_sbt_inv',
#             'objects': http.request.env['api_sbt_inv.api_sbt_inv'].search([]),
#         })

#     @http.route('/api_sbt_inv/api_sbt_inv/objects/<model("api_sbt_inv.api_sbt_inv"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('api_sbt_inv.object', {
#             'object': obj
#         })

# -*- coding: utf-8 -*-
import json, datetime, base64
from odoo import http
from odoo.http import request, Response
from datetime import datetime


class ApiSbtInv(http.Controller):
    @http.route('/api_sbt_inv/api_sbt_inv/', auth='public')
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

    def getRecord(self, model, field, wms):
        record = request.env[model].search([(field,'=',wms)])
        if record[field] == wms:
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

    @http.route('/api/createasn', type='json', auth='user', methods=['POST'])
    def post_rcpt(self, rcpt):
        created = 0
        error = {}
        warn_cnt = 1
        rcpt_lines = []
        is_error = False
        response_msg = "Failed to create GRN!"
        message = {}
        line_details = []
        is_partial = False
        
#        try:
        for rec in rcpt:
            #check poNo
            if rec['poNo'] == "":
                error["Error"] = "Field ownerReference is blank"
                is_error = True
                break

            po = self.getRecord(model="purchase.order", field="name", wms=rec['poNo'])
            if po == -1:
                error["Error"] = "poNo does not exist"
                is_error = True
                break

            #check receipt
            odoo_receipt = request.env["stock.picking"].search(['&','&',('origin', '=', rec['poNo']), ('picking_type_id', '=', 1), ('state', '=', 'assigned')])
            if odoo_receipt['origin'] != rec['poNo']:
                error["Error"] = "Receipt does not exist"
                is_error = True
                break

            #DocumentTransCode
            if rec['documentTransCode'] == "":
                error["Error"] = "Field documentTransCode is blank"
                is_error = True
                break

            #receiptDate
            if rec["receiptDate"] == "":
                receipt_date = ""
            else:
                try:
                    receipt_date = datetime.strptime(rec["receiptDate"], '%d/%m/%Y').date()
                except ValueError:
                    error["Error"] = "Wrong date format on receiptDate"
                    is_error = True
                    break

            #Receipt Line
            for line in rec['details']:
                temp_product = 0

                #ownerReference
                if line['ownerReference'] == "":
                    error["Error"] = "Field ownerReference is blank"
                    is_error = True
                    break

                #inwardLineOptChar1
                if line['inwardLineOptChar1'] == "":
                    error["Error"] = "Field inwardLineOptChar1 is blank"
                    is_error = True
                    break

                #product
                if line['product'] == "":
                    error["Error"] = "Field product is blank"
                    is_error = True
                    break

                temp_product = self.getRecord(model="product.product", field="default_code", wms=line['product'])
                if temp_product == -1:

                    created_product = request.env['product.product'].create({
                        "type": "product",
                        "default_code": line['product'],
                        "name": line['product'],
                        "tracking": "lot",
                        "use_expiration_date": 1,
                        "company_id": 1
                    })

                    temp_product = created_product['id']

                    warn_str = "Message " + str(warn_cnt)
                    error[warn_str] = "Product " + line['product'] + " has been created"
                    warn_cnt += 1

                for det in line['lineDetails']:

                    #Check quantityReceived
                    if det['quantityReceived'] == "":
                        error["Error"] = "Field quantityReceived is blank"
                        is_error = True
                        break

                    #Check expiryDate
                    if det['expiryDate'] == "":
                        expiry_date = ""
                    else:
                        try:
                            expiry_date = datetime.strptime(det['expiryDate'], '%d/%m/%Y').date()
                        except ValueError:
                            error["Error"] = "Wrong date format on expiryDate"
                            is_error = True
                            break

                    #Check stockStatusCode
                    if det['stockStatusCode'] == "":
                        error["Error"] = "Field stockStatusCode is blank"
                        is_error = True
                        break

                    #Check lotNo
                    if det['lotNo'] == "":
                        error["Error"] = "Field lotNo is blank"
                        is_error = True
                        break

                    temp_lot = request.env["stock.production.lot"].search(['&',("product_id",'=',temp_product),("name", '=', det['lotNo'])])
                    if temp_lot['name'] != det['lotNo']:
                        temp_lot = request.env['stock.production.lot'].create({
                            "product_id": temp_product,
                            "name": det["lotNo"],
                            "company_id": 1
                        })

                    line_detail = request.env['stock.move.line'].create({
                        "product_id": temp_product,
                        "product_uom_id": 1,
                        "location_id": 4,
                        "location_dest_id": 8,
                        "lot_id": temp_lot['id'],
                        "expiration_date": expiry_date,
                        "qty_done": det["quantityReceived"],
                        "company_id": 1,
                        "state": "done"
                    })

                    line_details.append(line_detail['id'])

                stock_move = request.env['stock.move'].search(['&',('origin','=',rec['poNo']),('x_studio_opt_char_1', '=', line["inwardLineOptChar1"])])
                if stock_move['origin'] != rec['poNo']:
                    error["Error"] = "Stock Move not found"
                    is_error = True
                    break
                    
                existing_detail = []
                for i in stock_move['move_line_nosuggest_ids']:
                    existing_detail.append(i['id'])
                    
                line_details += existing_detail

                stock_move['move_line_nosuggest_ids'] = line_details
                
                if stock_move['product_uom_qty'] == stock_move['quantity_done']:
                    stock_move['state'] = 'done'
                else:
                    is_partial = True


                if is_error == True:
                    break

            if is_error == True:
                break
            
            odoo_receipt['date_done'] = receipt_date
            odoo_receipt['x_studio_document_trans_code'] = rec["documentTransCode"]
            
            if is_partial == False:
                odoo_receipt['state'] = 'done'

            response_msg = "GRN updated successfully"
#        except Exception as e:
#            error["Error"] = str(e)
#            is_error = True

        if is_error == True:
#            Response.status = "400"
            pass
        else:
            Response.status = "200"
        
        message = {
            'response': response_msg, 
            'message': error
        }
        
        return message