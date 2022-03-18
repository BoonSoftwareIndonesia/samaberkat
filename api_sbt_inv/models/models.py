# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class api_sbt_inv(models.Model):
#     _name = 'api_sbt_inv.api_sbt_inv'
#     _description = 'api_sbt_inv.api_sbt_inv'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.http import request
import json, datetime, requests, base64, unicodedata
from datetime import datetime


class api_sbt_inv(models.Model):
    _name = 'api_sbt_inv.api_sbt_inv'
    _description = 'api_sbt_inv.api_sbt_inv'
    
    name = fields.Char(string="Message ID", required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'))
    incoming_msg = fields.Text(string="Incoming Message")
    response_msg = fields.Text(string="Response Message")
    status = fields.Selection([('new','New'),('process','Processing'),('success','Success'),('error','Error')])
    created_date = fields.Datetime(string="Created Date")
    response_date = fields.Datetime(string="Response Date")
    message_type = fields.Selection([('RCPT','CRT_RCPT'),('DO','CRT_DO'),('PO','DW_PO'),('SO','DW_SO')])
    incoming_txt = fields.Many2one('ir.attachment', string="Incoming txt", readonly=True)
    response_txt = fields.Many2one('ir.attachment', string="Response txt", readonly=True)
    raw_data = fields.Binary(string="Raw Data", attachment=True)
    raw_dataname = fields.Char(string="File Name")

    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('api.seq') or ('New')
        result = super(api_sbt_inv, self).create(vals)
        return result
    
class ApiController(models.Model):
    _inherit = "purchase.order"
    
    def api_dw_po(self, record):
        apiurl = "https://cloud1.boonsoftware.com/avi-trn-symphony-api/createasn"
        
        line_no = 1
        po_lines = []
        error = {}
        
        for line in record['order_line']:
            line['x_studio_opt_char_1'] = str(line_no)
            
            po_line = {
                "inwardLineOptChar1": line['x_studio_opt_char_1'],
                "inwardLineOptChar2": "" if line['x_studio_opt_char_2'] == False else line['x_studio_opt_char_2'],
                "product": record['product_id']['name'],
                "quantityOrdered": str(line['product_qty']),
                "uomCode": line['product_uom']['name'],
                "stockStatusCode": "" if line['x_studio_stock_status_code'] == False else line['x_studio_stock_status_code']
            }
            line_no += 1
            
            po_lines.append(po_line)
        
        
        payload = {
            "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJpZCIsImlhdCI6MTYxMTYzNzI3NCwic3ViIjoiaWQiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0IiwiYXVkIjoib2N0cyIsImV4cCI6MTYxMTcyMzY3NH0.bB2S1bNFxf_D0s8Fp2BGTXNc9CRNjEiRqyWFBNDzZ4c",
            "asn": [
                {
                    "ownerReferences": "" if record['x_studio_owner_reference'] == False else record['x_studio_owner_reference'],
                    "poNo": "" if record['name'] == False else record['name'],
                    "supplierReferences": "" if record['partner_ref'] == False else record['partner_ref'],
                    "sender": "" if record['x_studio_sender'] == False else record['x_studio_sender'],
                    "documentTransCode": "" if record['x_studio_document_trans_code'] == False else record['x_studio_document_trans_code'],
                    "ownerCode": "" if record['x_studio_owner'] == False else record['x_studio_owner'],
                    "warehouseCode": "" if record['picking_type_id']['warehouse_id']['code'] == False else record['picking_type_id']['warehouse_id']['code'],
                    "poDate": "" if record['date_approve'] == False else datetime.strftime(record['date_approve'], '%d/%m/%Y'),
                    "expectedArrivalDate": "" if record['date_planned'] == False else datetime.strftime(record['date_planned'], '%d/%m/%Y'),
                    "otherReferences": "" if record['x_studio_other_reference'] == False else record['x_studio_other_reference'],
                    "remark1": "" if record['x_studio_remark_1'] == False else record['x_studio_remark_1'],
                    "doNo": "" if record['x_studio_do_number'] == False else record['x_studio_do_number'],
                    "asnLine": po_lines
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*"
        }
        
        #Create log
        try:
            api_log = request.env['api_sbt_inv.api_sbt_inv'].create({
                'status': 'new',
                'created_date': datetime.now(),
                'incoming_msg': payload,
                'message_type': 'PO'
            })

            api_log['status'] = 'process'
        except Exception as e:
            error['Error'] = str(e)
            is_error = True
        
        try:
            api_log['incoming_txt'] = request.env['ir.attachment'].create({
                'name': str(api_log['name']) + '_in.txt',
                'type': 'binary',
                'datas': base64.b64encode(bytes(str(payload), 'utf-8')),
                'res_model': 'api_sbt_inv.api_sbt_inv',
                'res_id': api_log['id'],
                'mimetype': 'text/plain'
            })
        except Exception as e:
            error['Error'] = str(e)
            is_error = True
        
#        try:
        r = requests.post(apiurl, data=json.dumps(payload), headers=headers)
#        except Exception as e:
#            is_error = True
#            api_log['status'] = 'error'
            
#        wms_response = base64.b64encode(bytes(str(r.text), 'utf-8'))
        
        api_log['response_msg'] = base64.b64encode(bytes(str(r.text), 'utf-8'))
        api_log['response_date'] = datetime.now()
        
        """if is_error == False:
            api_log['status'] = 'success'
        elif '"returnStatus":"-1"' in api_log['response_msg']:
            api_log['status'] = 'error'
        else:
            api_log['status'] = 'success'"""
        
        if r.status_code == 200:
            api_log['status'] = 'success'
        else:
            api_log['status'] = 'error'
        
        api_log['response_txt'] = request.env['ir.attachment'].create({
            'name': str(api_log['name']) + '_out.txt',
            'type': 'binary',
            'datas': base64.b64encode(bytes(str(r.text), 'utf-8')),
            'res_model': 'api_sbt_inv.api_sbt_inv',
            'res_id': api_log['id'],
            'mimetype': 'text/plain'
        })
        

class ApiController2(models.Model):
    _inherit = "sale.order"
    
    def api_dw_so(self, record):
        apiurl = "https://cloud1.boonsoftware.com/avi-trn-symphony-api/createso"
        
        line_no = 1
        so_lines = []
        
        for line in record['order_line']:
            line['x_studio_line_no'] = str(line_no)
            
            so_line = {
                "soLineOptChar1": line['x_studio_line_no'],
                "soLineOptChar2": "" if line['x_studio_opt_char_2'] == False else line['x_studio_opt_char_2'],
                "product": line['product_id']['default_code'],
                #"productDesc": record['product_id']['name'],
                "quantityOrder": str(int(line['product_uom_qty'])),
                "uomCode": line['product_uom']['name'],
                "lotNo": "LOT",
                "filterTransactionCode": "NM",
            }
            line_no += 1
            
            so_lines.append(so_line)
        
        
        payload = {
            "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJpZCIsImlhdCI6MTYxMTYzNzI3NCwic3ViIjoiaWQiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0IiwiYXVkIjoib2N0cyIsImV4cCI6MTYxMTcyMzY3NH0.bB2S1bNFxf_D0s8Fp2BGTXNc9CRNjEiRqyWFBNDzZ4c",
            "order":[
                {
                    "customerPO":"" if record['x_studio_customer_po'] == False else record['x_studio_customer_po'],
                    "reference":"" if record['name'] == False else record['name'],
                    "customerCode":"" if record['partner_id']["x_studio_internal_id"] == False else record['partner_id']["x_studio_internal_id"],
                    "soHeaderOptChar3":"",
                    "documentTransCode":"" if record['x_studio_document_trans_code'] == False else record['x_studio_document_trans_code'],
                    "orderDate":"" if record['date_order'] == False else datetime.strftime(record['date_order'], '%d/%m/%Y'),
                    "requestedDeliveryDate":"" if record['x_studio_request_delivery_date'] == False else datetime.strftime(record['x_studio_request_delivery_date'], '%d/%m/%Y'),
                    "ownerCode":"" if record['x_studio_owner_code'] == False else record['x_studio_owner_code'],
                    "warehouseCode": "" if record['warehouse_id']['code'] == False else record['warehouse_id']['code'],
                    "shipNo":"" if record['partner_shipping_id']["x_studio_internal_id"] == False else record['partner_shipping_id']["x_studio_internal_id"],
                    "shipAddress1":"" if record['partner_shipping_id']["street"] == False else record['partner_shipping_id']["street"],
                    "shipCity":"" if record['partner_shipping_id']["city"] == False else record['partner_id']["x_studio_internal_id"],
                    "shipZipCode":"" if record['partner_shipping_id']["zip"] == False else record['partner_shipping_id']["zip"],
                    "shipCountry":"" if record['partner_shipping_id']["country_id"]["name"] == False else record['partner_shipping_id']["country_id"]["name"],
                    "shipZone":"NA",
                    "shipRoute":"NA",
                    "shipArea":"SHIP",
                    "remark2":"" if record['x_studio_remark_1'] == False else record['x_studio_remark_1'],
                    "remark1":"" if record['x_studio_remark_2'] == False else record['x_studio_remark_2'],
                    "allocatequantityOrder":"TRUE",
                    "shipInFull":"FALSE",
                    "orderLine": so_lines
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*"
        }
        
        r = requests.post(apiurl, data=json.dumps(payload), headers=headers)
        
class ApiController3(models.Model):
    _inherit = "stock.quant"
    
    def api_dw_inv(self):
        apiurl = "https://cloud1.boonsoftware.com/trn_avi_api/inventorycompare"
        
        inv_lines = []
        inv = request.env['stock.quant'].search([("location_id.usage","=","internal")])
       
        for i in inv:
            inv_line = {
                 "warehouseCode":"AVI",
                 "ownerCode":"AVI",
                 "product": i["product_id"]["default_code"],
                 "lotNumber": i["lot_id"]["name"],
                 "serialNumber":i["lot_id"]["name"],
                 "expiryDate":i["lot_id"]["expiration_date"],
                 "qtyOnHand":i["inventory_quantity"],
                 "stockStatusCode":"NM"
            }
        
            inv_lines.append(inv_line)
            
        inv_dm = request.env['stock.quant'].search([("location_id","=", 16)])
       
        for i in inv_dm:
            inv_line = {
                 "warehouseCode":"AVI",
                 "ownerCode":"AVI",
                 "product": i["product_id"]["default_code"],
                 "lotNumber": i["lot_id"]["name"],
                 "serialNumber":i["lot_id"]["name"],
                 "expiryDate":i["lot_id"]["expiration_date"],
                 "qtyOnHand":i["inventory_quantity"],
                 "stockStatusCode":"DM"
            }
        
            inv_lines.append(inv_line)
       
        
        payload = {
            "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJpZCIsImlhdCI6MTYxMTYzNzI3NCwic3ViIjoiaWQiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0IiwiYXVkIjoib2N0cyIsImV4cCI6MTYxMTcyMzY3NH0.bB2S1bNFxf_D0s8Fp2BGTXNc9CRNjEiRqyWFBNDzZ4c",
            "ivdList":[
                { 
                  "ownerCode":"AVI",
                  "documentType":"Upload Inventory",
                  "ivd": inv_lines
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*"
        }
        
        r = requests.post(apiurl, data=json.dumps(payload), headers=headers)
#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

