# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
import calendar


class SimpananDetails(models.Model):
    _name = 'simpanan.details'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    # name_2 = fields.Char(string='Name 2', required=True, copy=False, readonly=True, index=True,
    #                      default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')],
                             default='draft', readonly=True)

    date_plan = fields.Date(string='Date Plan', default=fields.Date.today(), readonly=True)
    simpanan_id = fields.Many2one('simpanan', readonly=True )
    partner_id = fields.Many2one(related='simpanan_id.partner_id', string='Customer', readonly=True)
    policy_id = fields.Many2one(related='simpanan_id.master_simpanan_id', string='Master Simpanan', readonly=True)
    bunga_persen = fields.Float(related='simpanan_id.bunga_persen',string='Bunga %', readonly=True)
    # employee_id = fields.Many2one(related='insurance_id.employee_id', string='Agent', readonly=True)
    amount = fields.Float(string='Jumlah')

    type_simpanan = fields.Selection([('inbound', 'InBound'), ('outbound','OutBound')],
                            readonly=True, default='inbound')
    
    invoice_id = fields.Many2one('account.move', string='Invoice', readonly=True, copy=False)
    account_move_id = fields.Many2one('account.move', string='Account', readonly=True, copy=False)

    note_field = fields.Html(string='Note')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('simpanan.details') or 'New'

        if vals.get('type_simpanan') == 'outbound':
            self.amount = (0 - self.amount) if self.amount > 0 else self.amount
            # for line in vals.get('line_ids'):
            #     line[2]['amount'] = line[2]['amount'] * -1 if line[2]['amount'] > 0 else line[2]['amount']
                


        return super(SimpananDetails, self).create(vals)


    def create_invoice(self):
        if not self.invoice_id:
            invoice_val = self.env['account.move'].create({
                                'move_type': 'in_invoice',
                                'partner_id': self.partner_id.id,
                                'invoice_user_id': self.env.user.id,
                                'simpanan_details_id': self.id,
                                'invoice_origin': self.name,
                                'invoice_line_ids': [(0, 0, {
                                    'name': 'Invoice For Simpanan Details',
                                    'quantity': 1,
                                    'price_unit': self.amount,
                                    'account_id': 41,
                                })],
                            })
            self.invoice_id = invoice_val


    def action_journal_simpanan_detail(self):
        if self.account_move_id:
            raise UserError(_("Sudah ada journal"))
        elif self.amount != 0:
            moveObj = self.env['account.move']
            account_id = self.policy_id.account_id.id
            account_debit = self.policy_id.account_id_in.id
            account_credit = self.policy_id.account_id_out.id
            journal = self.policy_id.journal_id.id
            # if self.amount > 0:
            #     saldo = self.amount
            # else:
            #     saldo = -1*self.amount
            label = 'simpanan'
            data = []
            for a in range(2):
                if self.type_simpanan == 'inbound':
                    if a == 0:
                        acc_id = account_debit
                        label = 'simpanan inbound'
                        saldo = self.amount
                    else:
                        acc_id = account_id
                        label = 'simpanan inbound'
                        saldo = self.amount
                else:
                    if a == 0:
                        acc_id = account_id
                        label = 'simpanan outbound'
                        saldo = -1*self.amount
                    else:
                        acc_id = account_credit
                        label = 'simpanan outbound'
                        saldo = -1*self.amount

                data.append((0,0,{
                    'account_id' : acc_id,
                    'partner_id' : self.partner_id.id,
                    'debit' : saldo if a == 0 else 0,
                    'credit' : 0 if a == 0 else saldo,
                    'name' : label,
                }))
            if self.amount != 0:
                idmove = moveObj.create({
                    'date' : fields.Date.today(),
                    'journal_id' : journal,
                    'ref' : self.simpanan_id.name,
                    'simpanan_id' : self.simpanan_id.id,
                    'line_ids' : data,

                })
                # idmove = moveOvj.create(val)
                self.account_move_id = idmove
                self.state = 'posted'

            # moveOvj = self.env['account.move']
            # val = {
            #     'partner_id': self.partner_id.id,
            #     'date': datetime.now(),
            #     'journal_id': self.policy_id.journal_id.id,
            #     # 'move_type': 'in_invoice' if self.angsuran_ke == 0 else 'out_invoice',
            #     'simpanan_id': self.simpanan_id.id,
            #     'simpanan_details_id': self.id,
            #     'invoice_line_ids': [(0,0,{
            #         'name': 'Simpanan Detail',
            #         'quantity': 1,
            #         'price_unit': self.amount
            #     })]
            # }
            # idmove = moveOvj.create(val)
            # self.account_move_id = idmove
            # self.create_invoice()
            # self.state = 'posted'



            # invoice_val = self.env['account.move'].create({
            #                     'move_type': 'in_invoice',
            #                     'partner_id': self.partner_id.id,
            #                     'invoice_user_id': self.env.user.id,
            #                     'pinjaman_details_id': self.id,
            #                     'invoice_origin': self.pinjaman_id,
            #                     'invoice_line_ids': [(0, 0, {
            #                         'name': 'Angsuran Pinjaman Details',
            #                         'quantity': 1,
            #                         'price_unit': self.actual_angsuran,
            #                         'account_id': 41,
            #                     })],
            #                 })
            # self.account_move_id = invoice_val
        else:
            raise UserError(_("Jumlah tidak boleh nol..."))


    def action_batal_journal_simpanan_detail(self):
        if self.amount != 0:
            self.state = 'draft'
            # self.pinjaman_id.hide_inv_button = True
        else:
            raise UserError(_("Jumlah tidak boleh nol..."))