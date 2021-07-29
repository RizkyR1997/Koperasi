# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    expenses_id = fields.Many2one("account.expenses", "Expenses")


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    ##  @api.multi
    # def write(self, vals):
    #     result = super(AccountMoveLine, self).write(vals)
    #     for rec in self:
    #         if rec.line_ids.expenses_id:
    #             for detail in self:
    #                 statement_id = detail.statement_id.id
    #                 statement_line_id = detail.statement_line_id.id
    #                 amount = detail.statement_line_id.amount
    #                 if statement_id and statement_line_id:
    #                     rec.move_id.expenses_id.write({
    #                         'statement_id': statement_id,
    #                         'statement_line_id': statement_line_id,
    #                         'kasbon': amount,
    #                         'selisih': rec.move_id.expenses_id.total + amount
    #                     })

            # print('expenses_id=>', str(rec.move_id.expenses_id.id) + ', statement_id=' + str(
            #     rec.statement_id.id) + ', statement_line_id=' + str(rec.statement_line_id.id))

        # return result


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

   #  @api.multi
    def write(self, vals):
        result = super(AccountPartialReconcile, self).write(vals)
        for rec in self:
            if rec.credit_move_id.move_id.expenses_id:
                rec.credit_move_id.move_id.expenses_id.state = 'reconcile'

            if rec.debit_move_id.move_id.expenses_id:
                rec.debit_move_id.move_id.expenses_id.state = 'reconcile'

        return result

   #  @api.multi
    def unlink(self):
        for rec in self:
            if rec.credit_move_id.move_id.expenses_id:
                rec.credit_move_id.move_id.expenses_id.state = 'confirm'
                rec.credit_move_id.move_id.expenses_id.statement_id = False
                rec.credit_move_id.move_id.expenses_id.statement_line_id = False
                rec.credit_move_id.move_id.expenses_id.kasbon = 0
                rec.credit_move_id.move_id.expenses_id.selisih = 0
            if rec.debit_move_id.move_id.expenses_id:
                rec.debit_move_id.move_id.expenses_id.state = 'confirm'
                rec.debit_move_id.move_id.expenses_id.statement_id = False
                rec.debit_move_id.move_id.expenses_id.statement_line_id = False
                rec.debit_move_id.move_id.expenses_id.kasbon = 0
                rec.debit_move_id.move_id.expenses_id.selisih = 0
        return super(AccountPartialReconcile, self).unlink()