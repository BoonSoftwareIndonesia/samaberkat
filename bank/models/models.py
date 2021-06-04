#  -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class bank(models.Model):
    
    _inherit = 'account.bank.statement'
    
    x_type = fields.Selection([('in','In'),('out','Out')])
    
    # Override function to calculate computed balance in the bank statement
    # If the bank type is 'out', then the computed balance will be start balance - total entry
    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real', 'x_type')
    def _end_balance(self):
        for statement in self:
            if statement.x_type == 'out':
                statement.total_entry_encoding = sum([line.amount for line in statement.line_ids])
                statement.balance_end = statement.balance_start - statement.total_entry_encoding
                statement.difference = statement.balance_end_real - statement.balance_end
            else:
                statement.total_entry_encoding = sum([line.amount for line in statement.line_ids])
                statement.balance_end = statement.balance_start + statement.total_entry_encoding
                statement.difference = statement.balance_end_real - statement.balance_end
                
    
    # This function used to raise warning message if the user input negative quantity in the amount
    # User should not input negative quantity because we have seperated the screen for in and out
    @api.onchange('line_ids')
    def _onchange_amount(self):
        if self.journal_id.type == 'bank':
            for line in self.line_ids:
                if line.amount < 0:
                    raise UserError('Please input positive value')
    
#     _name = 'bank.bank'
#     _description = 'bank.bank'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
