from odoo import models, fields, api

class TrialNewBalance_new(models.Model):
    _name = 'trial.balance.new'
    # _order = "code asc"
    _auto = False

    account_id  = fields.Many2one('account.account', string='Account')
    code = fields.Char(string='Code')
    description = fields.Char(string='Description')
    account_type = fields.Many2one('account.account.type', string='Account Type')
    opening = fields.Float(string='Opening')
    debit = fields.Float(string='Debit')
    credit = fields.Float(string='Credit')
    balance = fields.Float(string='Balance')

