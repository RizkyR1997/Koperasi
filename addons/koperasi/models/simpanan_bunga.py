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
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class PinjamanPelunasan(models.Model):
    _name = 'simpanan.bunga'

    name = fields.Char(string='No Pelunasan', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validate','Validate'), ('posted', 'Posted')],
                             readonly=True, default='draft')
    date = fields.Date(string='Tanggal Validasi', default=fields.Date.today(), required=True)
    bunga_detail_ids = fields.One2many('simpanan.bunga.detail', 'simpanan_bunga_id', string='Simpanan Detail')

    total_saldo_akhir = fields.Float(string='Total Saldo Akhir', compute='_compute_simpanan_bunga_')
    total_jumlah_bunga = fields.Float(string='Total Bunga Simpanan', compute='_compute_simpanan_bunga_')

    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)

    note_field = fields.Html(string='Note')
    month_years = fields.Char(string='Month years', readonly=True)
    
    
    def action_confirm(self):
        self.state = 'confirmed'

    def action_get_transaksi(self):
        self.state = 'draft'

    def action_validate(self):
        self.state = 'validate'

    def action_posted(self):
        self.state = 'posted'

    def action_get_trasaction(self):
        data = []
        moveObj = self.env['simpanan']
        # movePelunasanIds = moveObj.search([]).ids
        SimpananIds = moveObj.search([('state','=','done')])
        # self.pelunasan_detail_ids = [(4,0,movePelunasanIds)]buat Many2many

        for a in SimpananIds:            
            value = {
                'simpanan_bunga_id' : self.id,
                'simpanan_id' : a.id,
                'saldo_akhir': a.saldo_akhir,
                'jumlah_bunga': (a.saldo_akhir*a.bunga_persen)/100
                # 'type_pelunasan': 'cash',
                # 'status': 'unpaid',
                # 'rencana_angsuran': -abs(self.jumlah_pinjaman) if noUrut == 0 else (self.jumlah_pokok_perbulan + self.jumlah_jasa_perbulan ),
                # 'saldo_pinjaman': saldoPinjaman,
                # 'jumlah_pokok_perbulan': 0 if noUrut == 0 else (self.jumlah_pokok_perbulan),
                # 'jumlah_jasa_perbulan': 0 if noUrut == 0 else (self.jumlah_jasa_perbulan )
            }
            # noUrut += 1
            data.append((0,0,value))
        self.bunga_detail_ids = data
        self.state = 'confirmed'

    @api.depends('bunga_detail_ids')
    def _compute_simpanan_bunga_(self):
        for rec in self:
            rec.total_saldo_akhir = sum(line.saldo_akhir for line in rec.bunga_detail_ids)
            rec.total_jumlah_bunga = sum(line.jumlah_bunga for line in rec.bunga_detail_ids)


    def action_posted(self):
        data = []
        moveObj = self.env['simpanan.details']
        # movePelunasanIds = moveObj.search([]).ids
        # SimpananIds = moveObj.search([('state','=','done')])
        # # self.pelunasan_detail_ids = [(4,0,movePelunasanIds)]buat Many2many

        for a in self.bunga_detail_ids:
            value = {
                'simpanan_id' : a.simpanan_id.id,
                'date_plan': a.date,
                'amount': a.jumlah_bunga,
                'type_simpanan': 'inbound',
                'amount': a.jumlah_bunga,
                'note_field': self.note_field,
                'state': 'draft',
                'account_move_id': self.account_move_id.id
            }
            moveObj.create(value)
        self.state = 'posted'
        # di balik postdulu baru validate

    def action_validate(self):
        if self.total_jumlah_bunga > 0:
            moveObj = self.env['account.move']
            account_id = 165
            # account_debit = self.policy_id.account_id_in.id
            # account_credit = self.policy_id.account_id_out.id
            journal = 11
            # if self.amount > 0:
            #     saldo = self.amount
            # else:
            #     saldo = -1*self.amount
            tot_bunga = self.total_jumlah_bunga
            label = 'Bunga Simpanan'
            data = []
            data.append((0,0,{
                    'account_id' : account_id,
                    # 'partner_id' : self.partner_id.id,
                    'debit' : 0,
                    'credit' : tot_bunga,
                    'name' : 'Total Bunga',
                }))
            for a in self.bunga_detail_ids:
                data.append((0,0,{
                    'account_id' : a.master_simpanan_id.account_id_bunga.id,
                    'partner_id' : a.partner_id.id,
                    'debit' : a.jumlah_bunga,
                    'credit' : 0,
                    'name' : label,
                }))
            if not self.account_move_id:
                idmove = moveObj.create({
                    'date' : fields.Date.today(),
                    'journal_id' : journal,
                    'ref' : self.name,
                    # 'simpanan_id' : self.simpanan_id.id,
                    'line_ids' : data,

                })
                # idmove = moveOvj.create(val)
                self.account_move_id = idmove
                self.state = 'validate'
            # di balik postdulu baru validate

    def action_view_journal(self):
        self.ensure_one()
        # if self.pos_order_ids.filtered(lambda order: order.state != 'cancel'):
        #     action = self.env.ref('point_of_sale.action_pos_pos_form')
        #     view_id = self.env.ref('point_of_sale.view_pos_pos_form')
        #     ids = self.pos_order_ids.filtered(lambda order: order.state != 'cancel').ids
        # elif self.invoice_ids.filtered(lambda inv: inv.state != 'cancel'):
        #     action = self.env.ref('account.action_invoice_tree1')
        #     view_id = self.env.ref('account.invoice_form')
        #     ids = self.invoice_ids.filtered(lambda inv: inv.state != 'cancel').ids
        # else :
        #     return False
        # return {
        #     'name': action.name,
        #     'help': action.help,
        #     'type': action.type,
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'views': [(view_id.id, 'form')],
        #     'view_id': view_id.id,
        #     'target': action.target,
        #     'res_model': action.res_model,
        #     'res_id': ids[0],
        # }

# 
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pinjaman.pelunasan') or 'New'
            date = datetime.strptime(vals.get('date'), "%Y-%m-%d")
            vals['month_years'] = date.strftime('%m%Y')
        return super(PinjamanPelunasan, self).create(vals)
    
    @api.constrains('month_years')
    def _month_years_unique(self):
        record = self.search([('month_years', '=', self.date.strftime('%m%Y')),('id','!=',self.id)])
        if record:
            raise ValidationError(_('Data untuk tanggal %s sudah pernah dibuat!') % (self.date))

class SimpananBungaDetail(models.Model):
    _name = 'simpanan.bunga.detail'

    # name = fields.Char(string='No Pelunasan', required=True, copy=False, readonly=True, index=True,
    #                    default=lambda self: _('New'))
    name = fields.Char('Description')
    status = fields.Selection([('unpaid', 'Unpaid'), ('paid','Paid')],
                             readonly=True, default='unpaid')
    simpanan_bunga_id = fields.Many2one('simpanan.bunga',)
    date = fields.Date(related='simpanan_bunga_id.date', string='Date', readonly=True)

    simpanan_id = fields.Many2one('simpanan', string='Simpanan', readonly=True)
    master_simpanan_id = fields.Many2one('master.simpanan', related='simpanan_id.master_simpanan_id', string='Master Simpanan')
    bunga_persen = fields.Float(related='simpanan_id.bunga_persen',string='Bunga %', readonly=True)    
    partner_id = fields.Many2one('res.partner', related='simpanan_id.partner_id', string='Anggota', readonly=True)
    
    saldo_akhir = fields.Float(string='Saldo Akhir', readonly=True)
    jumlah_bunga = fields.Float(string='Bunga Simpanan', readonly=True)
    
    