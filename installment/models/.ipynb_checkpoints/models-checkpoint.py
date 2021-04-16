# -*- coding: utf-8 -*-

from datetime import date, datetime
from odoo import models, fields, api


class installment(models.Model):
    _inherit = 'account.payment'

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
