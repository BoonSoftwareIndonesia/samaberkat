# -*- coding: utf-8 -*-

from odoo import models, fields, api


class api_sbt(models.Model):
    _name = 'api_sbt.api_sbt'
    _description = 'api_sbt.api_sbt'
    
    name = fields.Char(string="Message ID", required=True, copy=False, readonly=True, index=True, default=lambda self: ('New'))
    incoming_msg = fields.Text(string="Incoming Message")
    response_msg = fields.Text(string="Response Message")
    status = fields.Selection([('new','New'),('process','Processing'),('success','Success'),('error','Error')])
    created_date = fields.Datetime(string="Created Date")
    response_date = fields.Datetime(string="Response Date")
    message_type = fields.Selection([('ar','CRT_AR'),('ap','CRT_AP')])
    incoming_txt = fields.Many2one('ir.attachment', string="Incoming txt", readonly=True)
    raw_data = fields.Binary(string="Raw Data", attachment=True)
    raw_dataname = fields.Char(string="File Name")

    @api.model
    def create(self, vals):
        if vals.get('name', ('New')) == ('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('api.seq') or ('New')
        result = super(api_sbt, self).create(vals)
        return result

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
