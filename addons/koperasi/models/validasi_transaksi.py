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


class ValidasiTransaksi(models.Model):
    _name = 'validasi.transaksi'

    name = fields.Char(string='No Validasi', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validate','Validate'), ('posted', 'Posted')],
                             required=True, default='draft')
    
    date = fields.Date(string='Tanggal Validasi', default=fields.Date.today(), required=True)
    periode_bulan = fields.Char(string='Periode Bulan')
    
    
    pembayaran_angsuran_ids = fields.Many2many('account.move', 'pembayaran_angsuran_id', string='Pembayaran Angsuran')
    pelunasan_angsuran_ids = fields.Many2many('account.move', 'pelunasan_angsuran_id', string='Pelunasan Angsuran')
    pencairan_pinjaman_ids = fields.One2many('validasi.transaksi.pencairan.pinjaman', 'pencairan_pinjaman_id', string='Pencairan Pinjaman')
    simpanan_wajib_ids = fields.One2many('validasi.transaksi.simpanan.wajib', 'simpanan_wajib_id', string='Simpanan Wajib')
    simpanan_pokok_ids = fields.One2many('validasi.transaksi.simpanan.pokok', 'simpanan_pokok_id', string='Simpanan Pokok')
    simpanan_sukarela_ids = fields.One2many('validasi.transaksi.simpanan.sukarela', 'simpanan_sukarela_id', string='Simpanan Sukarela')
    simpanan_haritua_ids = fields.One2many('validasi.transaksi.simpanan.hari.tua', 'simpanan_hari_tua_id', string='Simpanan Hari Tua')
    simpanan_sukarela_05_ids = fields.One2many('validasi.transaksi.simpanan.sukarela05', 'simpanan_sukarela05_id', string='Simpanan Sukarela 0.5%')
    bunga_simpanan_ids = fields.One2many('validasi.transaksi.simpanan.bunga', 'simpanan_bunga_id', string='Bunga Simpanan')
    shu_transaksi_ids = fields.One2many('validasi.transaksi.shu', 'shu_transaksi_id', string='SHU Transaksi')

    journal_count = fields.Integer(string='Journal',default=1)


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

    
    def action_confirm(self):
        self.state = 'confirmed'

    def action_get_transaksi(self):
        self.state = 'draft'

    def action_validate(self):
        self.state = 'validate'

    def action_posted(self):
        self.state = 'posted'

    def action_get_transaction(self):
        moveObj = self.env['account.move']
        movePembayaranIds = moveObj.search([('journal_id','=',2),('state','=','draft')]).ids
        movePelunasanIds = moveObj.search([('journal_id','=',1),('state','=','draft')]).ids
        self.pembayaran_angsuran_ids = [(6,0,movePembayaranIds)]
        self.pelunasan_angsuran_ids = [(6,0,movePelunasanIds)]

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('validasi.transaksi') or 'New'
        return super(ValidasiTransaksi, self).create(vals)


class ValidasiTransaksiPembayaranAngsuran(models.Model):
    _name = 'validasi.transaksi.pembayaran.angsuran'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    pembayaran_angsuran_id = fields.Many2one('account.move', string='Pembayaran Angsuran')

class ValidasiTransaksiPelunasanAngsuran(models.Model):
    _name = 'validasi.transaksi.pelunasan.angsuran'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    pelunasan_angsuran_id = fields.Many2one('account.move', string='Pelunasan Angsuran')

class ValidasiTransaksiPencairanPinjaman(models.Model):
    _name = 'validasi.transaksi.pencairan.pinjaman'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    pencairan_pinjaman_id = fields.Many2one('account.move', string='Pencairan Pinjaman')

class ValidasiTransaksiSimpananWajib(models.Model):
    _name = 'validasi.transaksi.simpanan.wajib'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    simpanan_wajib_id = fields.Many2one('account.move', string='Simpanan Wajib')

class ValidasiTransaksiSimpananPokok(models.Model):
    _name = 'validasi.transaksi.simpanan.pokok'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    simpanan_pokok_id = fields.Many2one('account.move', string='Simpanan Pokok')

class ValidasiTransaksiSimpananSukarela(models.Model):
    _name = 'validasi.transaksi.simpanan.sukarela'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    simpanan_sukarela_id = fields.Many2one('account.move', string='Simpanan Sukarela')

class ValidasiTransaksiSimpananHariTua(models.Model):
    _name = 'validasi.transaksi.simpanan.hari.tua'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    simpanan_hari_tua_id = fields.Many2one('account.move', string='Simpanan Hari Tua')

class ValidasiTransaksiSimpananSukarela05(models.Model):
    _name = 'validasi.transaksi.simpanan.sukarela05'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    simpanan_sukarela05_id = fields.Many2one('account.move', string='Simpanan Sukarela 0.5%')

class ValidasiTransaksiSimpananBunga(models.Model):
    _name = 'validasi.transaksi.simpanan.bunga'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    simpanan_bunga_id = fields.Many2one('account.move', string='Bunga Simpanan')

class ValidasiTransaksiShu(models.Model):
    _name = 'validasi.transaksi.shu'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    validasi_id = fields.Many2one('validasi.transaksi')
    shu_transaksi_id = fields.Many2one('account.move', string='SHU Transaksi')