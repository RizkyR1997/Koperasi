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


class PinjamanDetails(models.Model):
    _name = 'pinjaman.details'

    name = fields.Char(string='Description', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('on_progress','On Progress'), ('done','Done'), ('closed', 'Closed')],
                             required=True, default='draft')
    
    pinjaman_id = fields.Many2one('pinjaman', required=True, readonly=True)
    partner_id = fields.Many2one(related='pinjaman_id.partner_id', string='Customer', readonly=True)
    policy_id = fields.Many2one(related='pinjaman_id.master_pinjaman_id', string='Master Pinjaman', readonly=True)
    # employee_id = fields.Many2one(related='insurance_id.employee_id', string='Agent', readonly=True)

    angsuran_ke = fields.Integer(string='Angsuran Ke', readonly=True)
    tgl_angsuran = fields.Date(string='Tanggal Angsuran', readonly=True)
    type_pinjaman = fields.Selection([('inbound', 'InBound'), ('outbound','OutBound')],
                             required=True, default='inbound', readonly=True)
    type_pelunasan = fields.Selection([('cash', 'Cash'), ('transfer','Transfer'), ('payroll','Payroll')],
                             required=True, default='cash', readonly=True)
    jumlah_pokok = fields.Float(related='pinjaman_id.jumlah_angsuran', string='Jumlah Pokok', readonly=True)
    jumlah_jasa = fields.Float(string='Jumlah Jasa', readonly=True)
    jumlah_angsuran = fields.Float(string='Jumlah Angsuran', readonly=True)
    rencana_angsuran = fields.Float(string='Rencana Angsuran', readonly=True)
    actual_angsuran = fields.Float(string='Actual Angsuran')
    saldo_pinjaman = fields.Float(string='Saldo Pinjaman', readonly=True)
    status = fields.Selection([('unpaid', 'Unpaid'), ('paid','Paid')],
                             required=True, default='unpaid', readonly=True)
    
    invoice_id = fields.Many2one('account.move', string='Invoiced', readonly=True, copy=False)
    note_field = fields.Html(string='Comment')
    jumlah_pokok_perbulan = fields.Float(string='Angsuran Pokok', readonly=True)
    jumlah_jasa_perbulan = fields.Float(string='Angsuran Jasa', readonly=True)
    # jumlah_pokok_perbulan = fields.Float(string='Angsuran Pokok', related="pinjaman_id.jumlah_pokok_perbulan")
    # jumlah_jasa_perbulan = fields.Float(string='Angsuran Jasa', related="pinjaman_id.jumlah_jasa_perbulan")
    nunggak_hari = fields.Integer(string='Nunggak (Hari)', readonly=True)

    account_move_id = fields.Many2one('account.move', readonly=True)
    pelunasan_id = fields.Many2one('pinjaman.pelunasan', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pinjaman.details') or 'New'
        return super(PinjamanDetails, self).create(vals)


    def create_invoice(self):
        if not self.invoice_id:
            invoice_val = self.env['account.move'].create({
                                'move_type': 'out_invoice',
                                'partner_id': self.partner_id.id,
                                'invoice_user_id': self.env.user.id,
                                'pinjaman_details_id': self.id,
                                'invoice_origin': self.pinjaman_id,
                                'invoice_line_ids': [(0, {
                                    'name': 'Angsuran Pinjaman Details',
                                    'quantity': 1,
                                    'price_unit': self.actual_angsuran,
                                    'account_id': 41,
                                })],
                            })
            self.invoice_id = invoice_val


    

    def action_bayar_angsuran(self):
        if self.actual_angsuran > 0:
            moveObj = self.env['account.move']        
            # account_debit = self.pinjaman_id.master_pinjaman_id.account_id_in.id
            # account_credit = self.pinjaman_id.master_pinjaman_id.account_id_out.id
            journal = self.pinjaman_id.master_pinjaman_id.journal_id.id
        
            saldo = 0
            label = ''
            data = []
            for a in range(3):
                if a == 0:
                    saldo = self.actual_angsuran
                    label = 'Bayar Angsuran'
                    account_id = self.pinjaman_id.master_pinjaman_id.account_id_in.id
                elif a == 1:
                    saldo = self.jumlah_pokok_perbulan
                    label = 'Bayar Pokok'
                    account_id = self.pinjaman_id.master_pinjaman_id.account_id2.id
                else:
                    saldo = self.actual_angsuran-self.jumlah_pokok_perbulan
                    label = 'Bayar Jasa'
                    account_id = self.pinjaman_id.master_pinjaman_id.account_income.id
                
                data.append((0,0,{
                    'account_id' : account_id,
                    'partner_id' : self.partner_id.id,
                    'debit' : saldo if a == 0 else 0,
                    'credit' : 0 if a == 0 else saldo,
                    'name' : label,
                }))
            if self.actual_angsuran > 0:
                idmove = moveObj.create({
                    'date' : fields.Date.today(),
                    'journal_id' : journal,
                    'ref' : self.pinjaman_id.name + '- Angsuran Ke ' + str(self.angsuran_ke),
                    'pinjaman_id' : self.pinjaman_id.id,
                    'line_ids' : data,
                })
            self.status = 'paid'
            self.account_move_id = idmove

            self.action_bayar_angsuran_kasbank()

        else:
            raise UserError(_("Jumlah angsuran harus lebih besar dari nol..."))

    def action_bayar_angsuran_kasbank(self):
        if self.actual_angsuran > 0:
            moveObj = self.env['account.move']        
            # account_debit = self.pinjaman_id.master_pinjaman_id.account_id_in.id
            # account_credit = self.pinjaman_id.master_pinjaman_id.account_id_out.id
            journal = self.pinjaman_id.master_pinjaman_id.journal_id.id
        
            saldo = 0
            label = ''
            data = []
            for a in range(2):
                if a == 0:
                    saldo = self.actual_angsuran
                    label = 'Bayar Angsuran'
                    account_id = self.pinjaman_id.master_pinjaman_id.account_id.id
                else:
                    saldo = self.actual_angsuran
                    label = 'Clearing Angsuran'
                    account_id = self.pinjaman_id.master_pinjaman_id.account_id_in.id
                
                data.append((0,0,{
                    'account_id' : account_id,
                    'partner_id' : self.partner_id.id,
                    'debit' : saldo if a == 0 else 0,
                    'credit' : 0 if a == 0 else saldo,
                    'name' : label,
                }))
            if self.actual_angsuran > 0:
                idmove = moveObj.create({
                    'date' : fields.Date.today(),
                    'journal_id' : journal,
                    'ref' : self.pinjaman_id,
                    'pinjaman_id' : self.pinjaman_id.id,
                    'line_ids' : data,
                })
            # self.status = 'paid'
            # self.account_move_id = idmove

        else:
            raise UserError(_("Jumlah angsuran harus lebih besar dari nol..."))

    def action_batal_bayar_angsuran(self):
        if self.actual_angsuran > 0:
            self.status = 'unpaid'
            # self.pinjaman_id.hide_inv_button = True
        else:
            raise UserError(_("Jumlah angsuran harus lebih besar dari nol..."))