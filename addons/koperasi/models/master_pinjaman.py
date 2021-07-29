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


class MasterPinjaman(models.Model):
    _name = 'master.pinjaman'

    name = fields.Char(string='Name', required=True)
    pinjaman_type = fields.Many2one('master.pinjaman.type', string='Pinjaman Type', required=True)
    payment_type = fields.Selection([('fixed', 'Fixed'), ('installment', 'Installment')],
                                    required=True, default='fixed')
    jasa_persen = fields.Float(string='Total Jasa %', compute='_compute_jasa_')
    jasa_persen_bulan = fields.Float(string='Jasa Per Bulan %')

    s_sukarela_persen = fields.Float(string='S. Sukarela %')
    j_sosial_persen = fields.Float(string='J. Sosial %')
    pinjaman_duration = fields.Integer(string='Duration in Month', required=True)
    note_field = fields.Html(string='Comment')

    account_id_in = fields.Many2one('account.account', string='Account In')
    #celear_angsur
    account_id_out = fields.Many2one('account.account', string='Account Out')
    # clearing_pinj
    account_id = fields.Many2one('account.account', string='Account Valuation')
    # kas
    account_id2 = fields.Many2one('account.account', string='Account Pinjaman')
    # pinjaman anggota
    journal_id = fields.Many2one('account.journal', string='Journal')
    

    account_diference = fields.Many2one('account.account', string='Account Difference')
    account_income = fields.Many2one('account.account', string='Account Income')
    # pend bunga
    account_expense = fields.Many2one('account.account', string='Account Expense')
    #biaya2

    @api.depends('pinjaman_duration')
    def _compute_jasa_(self):
        for rec in self:
            # if rec.pinjaman_duration > 0:
            if rec.jasa_persen_bulan > 0:
                rec.jasa_persen = (rec.pinjaman_duration * rec.jasa_persen_bulan)
            else:
                rec.jasa_persen = 0

            # if rec.jasa_persen > 0:
            #     rec.jasa_persen_bulan = ((rec.pinjaman_duration * rec.jasa_persen_bulan) / rec.pinjaman_duration)
            # else:    
            #     rec.jasa_persen_bulan = 0

            # if rec.jangka_waktu > 0:
            #     rec.jumlah_angsuran = (rec.jumlah_pinjaman / rec.jangka_waktu) + (((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu)
            # if rec.jangka_waktu > 0:
            #     rec.jumlah_jasa = (((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu)
            # rec.jumlah_pokok = rec.jumlah_pinjaman - (rec.s_sukarela_amount + rec.j_sosial_amount + rec.biaya_adm)
            # rec.sisa_pinjaman = rec.jumlah_pinjaman - rec.total_angsuran


class MasterPinjamanType(models.Model):
    _name = 'master.pinjaman.type'

    name = fields.Char(string='Name')


class MasterPinjamanPelunasan(models.Model):
    _name = 'master.pinjaman.pelunasan'

    name = fields.Char(string='Name')
    pinjaman_duration = fields.Integer(string='Duration in Month', required=True)
    angsuran_detail_ids = fields.One2many('master.pinjaman.pelunasan.detail', 'pelunasan_id', string='Detail Jasa Pelunasan')
    note_field = fields.Html(string='Comment')
    
class MasterPinjamanPelunasanDetail(models.Model):
    _name = 'master.pinjaman.pelunasan.detail'

    name = fields.Char(string='Name')
    pelunasan_id = fields.Many2one('master.pinjaman.pelunasan', string='Pelunasan')
    pinjaman_duration = fields.Integer(related='pelunasan_id.pinjaman_duration', string='Duration in Month', readonly=True)
    sisa_angsuran1 = fields.Integer(string='Sisa Angsuran Dari', required=True)
    sisa_angsuran2 = fields.Integer(string='Sisa Angsuran Sampai Ke', required=True)
    jumlah_kali_jasa = fields.Integer(string='Jumlah Kali Jasa', required=True)
