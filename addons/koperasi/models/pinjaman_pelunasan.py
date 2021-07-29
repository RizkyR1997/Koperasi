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


class PinjamanPelunasan(models.Model):
    _name = 'pinjaman.pelunasan'

    name = fields.Char(string='No Pelunasan', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validate','Validate'), ('posted', 'Posted')],
                             required=True, default='draft')
    date = fields.Date(string='Tanggal Validasi', default=fields.Date.today(), required=True)
    partner_id = fields.Many2one('res.partner', string='Anggota',)
    pinjaman_id = fields.Many2one('pinjaman')
    jangka_waktu = fields.Integer(related='pinjaman_id.jangka_waktu',string='Jangka Waktu', readonly=True)
    jumlah_pokok_perbulan = fields.Float(related='pinjaman_id.jumlah_pokok_perbulan',string='Jumlah Pokok PerBulan', readonly=True)
    jumlah_jasa_perbulan = fields.Float(related='pinjaman_id.jumlah_jasa_perbulan',string='Jumlah Jasa PerBulan', readonly=True)
    master_pinjaman_pelunasan_id = fields.Many2one('master.pinjaman.pelunasan.detail', readonly=True)
    jumlah_kali_jasa = fields.Integer(related='master_pinjaman_pelunasan_id.jumlah_kali_jasa' ,string='Jumlah Kali Jasa', readonly=True)

    jumlah_pelunasan = fields.Float(string='Jumlah Pelunasan', readonly=True, compute='_compute_pelunasan_')


    sisa_total_pokok = fields.Float(string='Sisa Pokok', compute='_compute_pelunasan_')
    sisa_total_jasa = fields.Float(string='Sisa Jasa', compute='_compute_pelunasan_')
    selisih_total = fields.Float(string='Selisih Total', compute='_compute_pelunasan_')

    pelunasan_detail_ids = fields.One2many('pinjaman.pelunasan.detail', 'pelunasan_id', string='Detail Pelunasan')

    note_field = fields.Html(string='Note')

    journal_count = fields.Integer(string='Journal',default=1)
    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    
    
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
        print('=======action_get_tra======')
        moveObj = self.env['pinjaman.details']
        # movePelunasanIds = moveObj.search([]).ids
        movePelunasanIds = moveObj.search([('pinjaman_id','=',self.pinjaman_id.id),('status','=','unpaid'),('type_pinjaman','=','inbound')])
        # self.pelunasan_detail_ids = [(4,0,movePelunasanIds)]buat Many2many
        pelunasanConfObj = self.env['master.pinjaman.pelunasan'].search([('pinjaman_duration','=',self.jangka_waktu)]).angsuran_detail_ids.filtered(lambda x : x.sisa_angsuran2 <= len(movePelunasanIds) and x.sisa_angsuran1 >= len(movePelunasanIds))
        self.master_pinjaman_pelunasan_id = pelunasanConfObj.id
        for i , a in enumerate(movePelunasanIds):            
            value = {
                'pelunasan_id' : self.id,
                'pinjaman_id' : a.pinjaman_id.id,
                'pinjaman_detail_id': a.id,
                'actual_angsuran': (self.jumlah_pokok_perbulan + self.jumlah_jasa_perbulan) if i < pelunasanConfObj.jumlah_kali_jasa and pelunasanConfObj.jumlah_kali_jasa != 0 else a.jumlah_pokok_perbulan,
                'type_pinjaman': a.type_pinjaman
                # 'type_pelunasan': 'cash',
                # 'status': 'unpaid',
                # 'rencana_angsuran': -abs(self.jumlah_pinjaman) if noUrut == 0 else (self.jumlah_pokok_perbulan + self.jumlah_jasa_perbulan ),
                # 'saldo_pinjaman': saldoPinjaman,
                # 'jumlah_pokok_perbulan': 0 if noUrut == 0 else (self.jumlah_pokok_perbulan),
                # 'jumlah_jasa_perbulan': 0 if noUrut == 0 else (self.jumlah_jasa_perbulan )
            }
            # noUrut += 1
            data.append((0,0,value))
        self.pelunasan_detail_ids = data
        self.state = 'confirmed'

    def action_validate(self):
        data = []
        moveObj = self.env['pinjaman.details']
        # movePelunasanIds = moveObj.search([]).ids
        PinjamanIds = moveObj.search([('state','=','done')])
        # # self.pelunasan_detail_ids = [(4,0,movePelunasanIds)]buat Many2many

        for a in self.pelunasan_detail_ids:            
            a.pinjaman_detail_id.write({'status' : 'paid','actual_angsuran': a.actual_angsuran,'pelunasan_id': a.pelunasan_id})
            # a.pinjaman_detail_id.action_bayar_angsuran()
            # value = {
            #     'pinjaman_id' : a.simpanan_id.id,
            #     'date_plan': a.date,
            #     'amount': a.jumlah_bunga,
            #     'type_simpanan': 'inbound',
            #     'amount': a.jumlah_bunga,
            #     'note_field': self.note_field,
            #     'state': 'draft'
            # }
            # moveObj.write([()])
        self.state = 'validate'

    def action_posted(self):
        data = []
        moveObj = self.env['pinjaman.details']
        # movePelunasanIds = moveObj.search([]).ids
        PinjamanIds = moveObj.search([('state','=','done')])
        # # self.pelunasan_detail_ids = [(4,0,movePelunasanIds)]buat Many2many

        for a in self.pelunasan_detail_ids:            
            # a.pinjaman_detail_id.write({'status' : 'paid','actual_angsuran': a.actual_angsuran,'pelunasan_id': a.pelunasan_id})
            a.pinjaman_detail_id.action_bayar_angsuran()
            # value = {
            #     'pinjaman_id' : a.simpanan_id.id,
            #     'date_plan': a.date,
            #     'amount': a.jumlah_bunga,
            #     'type_simpanan': 'inbound',
            #     'amount': a.jumlah_bunga,
            #     'note_field': self.note_field,
            #     'state': 'draft'
            # }
            # moveObj.write([()])
        # self.state = 'validate'
        self.state = 'posted'

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


    @api.depends('pelunasan_detail_ids','jumlah_kali_jasa','jumlah_jasa_perbulan')
    def _compute_pelunasan_(self):

        tot_angsur = 0

        for rec in self:
            # if rec.s_sukarela_persen > 0:
            #     rec.s_sukarela_amount = (rec.jumlah_pinjaman * rec.s_sukarela_persen)/100
            # if rec.j_sosial_persen > 0:
            #     rec.j_sosial_amount = (rec.jumlah_pinjaman * rec.j_sosial_persen)/100
            # if rec.jangka_waktu > 0:
            #     rec.jumlah_angsuran = (rec.jumlah_pinjaman / rec.jangka_waktu) + (((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu)
            # if rec.jangka_waktu > 0:
            #     rec.jumlah_jasa = (((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu)
            # rec.jumlah_pokok = rec.jumlah_pinjaman - (rec.s_sukarela_amount + rec.j_sosial_amount + rec.biaya_adm)
            
            # rec.sisa_angsuran = rec.jangka_waktu - rec.total_kali_angsuran
            # if rec.jangka_waktu > 0:
            #     rec.jumlah_pokok_perbulan = rec.jumlah_pinjaman / rec.jangka_waktu
            # else:
            #     rec.jumlah_pokok_perbulan = 0
            # if rec.jangka_waktu > 0:
            #     rec.jumlah_jasa_perbulan = ((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu
            # else:
            #     rec.jumlah_jasa_perbulan = 0
            

            # rec.sisa_total_pokok = sum(line.jumlah_pokok for line in rec.pelunasan_detail_ids.filtered(lambda x: x.status=='paid'))

            

            rec.sisa_total_pokok = sum(line.jumlah_pokok for line in rec.pelunasan_detail_ids)
            rec.sisa_total_jasa = sum(line.jumlah_jasa for line in rec.pelunasan_detail_ids)

            rec.jumlah_pelunasan = (rec.jumlah_kali_jasa*rec.jumlah_jasa_perbulan) + rec.sisa_total_pokok

            rec.selisih_total = rec.sisa_total_pokok + rec.sisa_total_jasa - rec.jumlah_pelunasan

            # if line.status='paid': 

            # for line in rec.pinjaman_detail_ids:
            #     tot_angsur =+ line.jumlah_pokok_perbulan
            #     if line.status = 'paid':
            #         tot_angsur =+ line.jumlah_pokok
            # rec.total_angsuran = tot_angsur

    # def action_posted(self):
    #     if self.account_move_id:
    #         raise UserError(_("Sudah ada journal"))
    #     elif self.jumlah_pelunasan > 0:
    #         moveOvj = self.env['account.move']
    #         val = {
    #             'partner_id': self.partner_id.id,
    #             'date': self.date,
    #             'journal_id': 2,
    #             'move_type': 'in_invoice',
    #             'pinjaman_id': self.pinjaman_id.id,
    #             # 'pinjaman_details_id': self.id,
    #             'invoice_line_ids': [(0,0,{
    #                 'name': 'Pelunasan Pinjaman',
    #                 'quantity': 1,
    #                 'price_unit': self.jumlah_pelunasan
    #             })]
    #         }
    #         idmove = moveOvj.create(val)
    #         self.account_move_id = idmove
    #         self.state = 'posted'
            
    #     else:
    #         raise UserError(_("Jumlah pelunasan harus lebih besar dari nol..."))

# 
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pinjaman.pelunasan') or 'New'
        return super(PinjamanPelunasan, self).create(vals)

class PinjamanPelunasanDetail(models.Model):
    _name = 'pinjaman.pelunasan.detail'

    # name = fields.Char(string='No Pelunasan', required=True, copy=False, readonly=True, index=True,
    #                    default=lambda self: _('New'))
    name = fields.Char('Description')
    status = fields.Selection([('unpaid', 'Unpaid'), ('paid','Paid')],
                             required=True, default='unpaid')
    pelunasan_id = fields.Many2one('pinjaman.pelunasan', required=True)
    pinjaman_id = fields.Many2one(related='pelunasan_id.pinjaman_id', string='Pinjaman', readonly=True)
    date = fields.Date(related='pelunasan_id.date', string='Date', readonly=True)
    pinjaman_detail_id = fields.Many2one('pinjaman.details', string='Pinjaman Detail', readonly=True)
    partner_id = fields.Many2one(related='pinjaman_id.partner_id', string='Anggota', readonly=True)
    policy_id = fields.Many2one(related='pinjaman_id.master_pinjaman_id', string='Master Pinjaman', readonly=True)
    angsuran_ke = fields.Integer(related='pinjaman_detail_id.angsuran_ke',string='Angsuran Ke', readonly=True)
    tgl_angsuran = fields.Date(related='pelunasan_id.date',string='Tanggal Angsuran', readonly=True)
    type_pinjaman = fields.Selection([('inbound', 'InBound'), ('outbound','OutBound')], readonly=True, related='pinjaman_detail_id.type_pinjaman',)
    type_pelunasan = fields.Selection([('cash', 'Cash'), ('transfer','Transfer'), ('payroll','Payroll')],
                             required=True, default='cash')
    jumlah_pokok = fields.Float(related='pinjaman_id.jumlah_pokok_perbulan', string='Jumlah Pokok')
    jumlah_jasa = fields.Float(related='pinjaman_id.jumlah_jasa_perbulan', string='Jumlah Jasa')
    jumlah_angsuran = fields.Float(related='pinjaman_id.jumlah_angsuran', string='Jumlah Angsuran')
    rencana_angsuran = fields.Float(related='pinjaman_detail_id.rencana_angsuran',string='Rencana Angsuran')
    actual_angsuran = fields.Float(string='Actual Angsuran')
    # saldo_pinjaman = fields.Float(string='Saldo Pinjaman')    
    