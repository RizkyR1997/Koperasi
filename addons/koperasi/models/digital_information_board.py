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
import logging

logger = logging.getLogger()



class DigitalInformationBoard(models.Model):
    _name = 'digital.information.board'
    _inherit = 'barcodes.barcode_events_mixin'

    name = fields.Char(string='Nomer', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('close', 'Closed')],
                             required=True, default='draft')
    
    date = fields.Datetime(string='Tanggal Informasi', default=fields.Date.today())
    
    partner_id = fields.Many2one('res.partner', string='Nama Anggota')
    no_anggota = fields.Char(related='partner_id.no_anggota',string='No Anggota')
    no_npk = fields.Char(related='partner_id.no_npk',string='NPK')
    rf_id = fields.Char(related='partner_id.rf_id',string='RFID')
    # nomor_anggota = fields.Char(string='No Anggota')

    simpanan_ids = fields.One2many('validasi.transaksi.simpanan', 'simpanan_id', string='Data Simpanan')
    pinjaman_ids = fields.One2many('validasi.transaksi.pinjaman', 'pinjaman_id', string='Data Pinjaman')
    bunga_simpanan_ids = fields.One2many('validasi.transaksi.simpanan.bunga', 'simpanan_bunga_id', string='Bunga Simpanan')
    shu_transaksi_ids = fields.One2many('validasi.transaksi.shu', 'shu_transaksi_id', string='SHU Transaksi')
    

    def action_get_transaksi(self):
        self.state = 'draft'

    def action_closed(self):
        self.state = 'close'

    def on_barcode_scanned(self, partner_id):
        logger.error("==================testtt===========")
        logger.error(partner_id)
        if self.state != 'draft' :
            raise Warning("Scan RFID hanya ketika status draft.")
        partner_id = self.env['res.partner'].search([
            ('rf_id','=',partner_id),
        ], limit=1)
        if not partner_id :
            logger.error("Barcode tdk ditemukan")
            raise Warning(_("Barcode tidak ditemukan."))
        self.partner_id = partner_id.id
        print('tes barcode')
        # self.lines += self.env['pos.quotation.line'].new({
        #     'lot_id': lot_id.id,
        #     'product_id': lot_id.product_id.id,
        #     'qty': lot_id.product_saldo,
        # })



class ValidasiTransaksiSimpanan(models.Model):
    _name = 'validasi.transaksi.simpanan'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date = fields.Datetime(string='Tanggal Jam', default=fields.Date.today(), required=True)
    information_id = fields.Many2one('digital.information.board')
    simpanan_id = fields.Many2one('simpanan', string='Simpanan')

class ValidasiTransaksiSimpananPokok(models.Model):
    _name = 'validasi.transaksi.pinjaman'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date = fields.Datetime(string='Tanggal Jam', default=fields.Date.today(), required=True)
    information_id = fields.Many2one('digital.information.board')
    pinjaman_id = fields.Many2one('pinjaman', string='Pinjaman')

class ValidasiTransaksiSimpananBunga(models.Model):
    _name = 'validasi.transaksi.simpanan.bunga'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date = fields.Datetime(string='Tanggal Jam', default=fields.Date.today(), required=True)
    information_id = fields.Many2one('digital.information.board')
    simpanan_bunga_id = fields.Many2one('account.move', string='Bunga Simpanan')

class ValidasiTransaksiShu(models.Model):
    _name = 'validasi.transaksi.shu'

    name = fields.Char(string='Name', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date = fields.Datetime(string='Tanggal Jam', default=fields.Date.today(), required=True)
    information_id = fields.Many2one('digital.information.board')
    shu_transaksi_id = fields.Many2one('account.move', string='SHU Transaksi')