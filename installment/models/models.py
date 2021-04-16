# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import models, fields, api


class installment(models.Model):
    _inherit = 'account.payment'
    
    x_installment = fields.Boolean(string='Installment')
    x_transaction = fields.Many2one('account.move', string='Transaction')
    x_next_due_date = fields.Date(string='Next Due Date')
    
    @api.onchange('x_transaction')
    def _onchange_payment(self):
        lines = []
        
        self.ref = self.x_transaction.name
        self.partner_id = self.x_transaction.partner_id
        
        for line in self.x_transaction.line_ids:
            temp = {}
            
            if line.date_maturity:
                temp['date_maturity'] = line.date_maturity
                temp['credit'] = line.credit
                temp['matching_number'] = line.matching_number
                temp['account_id'] = line.account_id
                lines.append(temp)
        
        lines.sort(key = lambda x:x['date_maturity'])
        
        for line in lines:
            if not line['matching_number']:
                self.x_next_due_date = line['date_maturity']
                self.amount = line['credit']
                self.destination_account_id = line['account_id']
                break
            else:
                continue
            break

#     _name = 'installment.installment'
#     _description = 'installment.installment'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class payment_term(models.Model):
    _inherit = 'account.payment.term'
    
    x_is_installment = fields.Boolean(string='Installment')