#  -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class bank(models.Model):
    
    _inherit = 'account.bank.statement'
    
    x_type = fields.Selection([('in','In'),('out','Out')], string='Bank Type')
                
    
    # This function is used to change the +/- of the line_ids.amount based on the x_type selected
    @api.onchange('line_ids', 'line_ids.amount', 'x_type')
    def _onchange_amount(self):
        for statement in self:
            for line in statement.line_ids:
                if statement.x_type == 'out':
                    if line.amount > 0:
                        line.amount *= -1
                else:
                    if line.amount < 0:
                        line.amount *= -1
    
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
