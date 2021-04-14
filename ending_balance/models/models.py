# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ending_balance(models.Model):
    _inherit = 'account.bank.statement'
    
    @api.onchange('balance_end')
    def _onchange_balance(self):
        self.balance_end_real = self.balance_end
#     _name = 'ending_balance.ending_balance'
#     _description = 'ending_balance.ending_balance'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
