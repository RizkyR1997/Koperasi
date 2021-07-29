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


class MasterSHU(models.Model):
    _name = 'master.shu'

    name = fields.Char(string='Name', required=True)
    ad_art = fields.Char(string='No AD/ART')
    date_start = fields.Date(string='Date Started', default=fields.Date.today(), required=True)
    end_date = fields.Date(string='Date End', default=fields.Date.today(), required=True)
    

    persen_shu_modal = fields.Float(string='SHU % Modal')
    persen_shu_simpanan = fields.Float(string='SHU % Simpanan')
    persen_shu_pinjaman = fields.Float(string='SHU % Pinjaman')
    persen_shu_cadangan = fields.Float(string='SHU % Cadangan')
    persen_shu_pengurus = fields.Float(string='SHU % Pengurus')
    persen_shu = fields.Float(string='SHU %', required=True)

    note_field = fields.Html(string='Comment')

    master_shu_detail_ids = fields.One2many('master.shu.detail', 'master_shu_id', string='Detail SHU')

    account_id = fields.Many2one('account.account', string='Account SHU')
    journal_id = fields.Many2one('account.journal', string='Journal SHU')
    account_id_in = fields.Many2one('account.account', string='Account SHU In')
    account_id_out = fields.Many2one('account.account', string='Account SHU Out')


    clossing_profit_id = fields.Many2one('account.account', string='Account Profit Loss')
    clossing_modal_id = fields.Many2one('account.account', string='Account Modal')
    clossing_simpanan_id = fields.Many2one('account.account', string='Account Simpanan')
    clossing_pinjaman_id = fields.Many2one('account.account', string='Account Pinjaman')
    clossing_cadangan_id = fields.Many2one('account.account', string='Account Cadangan')
    clossing_pengurus_id = fields.Many2one('account.account', string='Account Pengurus')

    clossing_pembulatan_id = fields.Many2one('account.account', string='Account Pembulatan')

class MasterShuDetail(models.Model):
    _name = 'master.shu.detail'

    name = fields.Char(string='Name')
    date = fields.Date(string='Date', default=fields.Date.today(), required=True)
    master_shu_id = fields.Many2one('master.shu')
    shu_komponen_id = fields.Many2one('master.shu.komponen')
    shu_persen = fields.Float(string='SHU %', required=True)


class ShuTransaksi(models.Model):
    _name = 'shu.transaksi'

    name = fields.Char(string='No Transaksi SHU', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date = fields.Date(string='Date', default=fields.Date.today(), required=True)
    shu_id = fields.Many2one('master.shu')
    date_start = fields.Date(related="shu_id.date_start",string='Date Started')
    end_date = fields.Date(related="shu_id.end_date",string='Date End')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('validate','Validate'), ('posted', 'Posted'), ('closed', 'Closed')],
                             default='draft', readonly = True)
    jum_anggota = fields.Integer(string='Jum Anggota')
    persen_shu_modal = fields.Float(related="shu_id.persen_shu_modal",string='SHU % Modal')
    persen_shu_simpanan = fields.Float(related="shu_id.persen_shu_simpanan",string='SHU % Simpanan')
    persen_shu_pinjaman = fields.Float(related="shu_id.persen_shu_pinjaman",string='SHU % Pinjaman')
    persen_shu_cadangan = fields.Float(related="shu_id.persen_shu_cadangan",string='SHU % Cadangan')
    persen_shu_pengurus = fields.Float(related="shu_id.persen_shu_pengurus",string='SHU % Pengurus')

    nilai_shu_modal = fields.Float(string='Nilai SHU Modal', compute='_compute_simpanan_bunga_')
    nilai_shu_simpanan = fields.Float(string='Nilai SHU Simpanan', compute='_compute_simpanan_bunga_')
    nilai_shu_pinjaman = fields.Float(string='Nilai SHU Pinjaman', compute='_compute_simpanan_bunga_')
    nilai_shu_cadangan = fields.Float(string='Nilai SHU Candangan', compute='_compute_simpanan_bunga_')
    nilai_shu_pengurus = fields.Float(string='Nilai SHU Pengurus', compute='_compute_simpanan_bunga_')
    # persen_shu = fields.Float(string='SHU %', required=True)

    amount_shu = fields.Float(string='Tot SHU / Profit Loss')
    amount_shu_simpanan = fields.Float(string='Tot Simpanan', compute='_compute_simpanan_bunga_')
    amount_shu_pinjaman = fields.Float(string='Tot Pinjaman', compute='_compute_simpanan_bunga_')

    account_move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    

    shu_transaksi_detail_ids = fields.One2many('shu.transaksi.line', 'shu_transaksi_id', string='Detail Transaksi SHU')

    tot_shu_dibagikan = fields.Float(string='Total SHU dibagikan', compute='_compute_simpanan_bunga_')

    tot_pembulatan_shu = fields.Float(string='Pembulatan SHU dibagikan', compute='_compute_simpanan_bunga_')

    journal_count = fields.Integer(string='Journal',default=1)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('shu.transaksi') or 'New'
        return super(ShuTransaksi, self).create(vals)

    @api.depends('shu_transaksi_detail_ids','amount_shu','persen_shu_modal','persen_shu_simpanan','persen_shu_pinjaman','persen_shu_cadangan')
    def _compute_simpanan_bunga_(self):
        for rec in self:
            rec.amount_shu_simpanan = sum(line.amount_shu_simpanan_anggota for line in rec.shu_transaksi_detail_ids)
            rec.amount_shu_pinjaman = sum(line.amount_shu_pinjaman_anggota for line in rec.shu_transaksi_detail_ids)
            rec.tot_shu_dibagikan = round(sum(line.amount_shu_anggota for line in rec.shu_transaksi_detail_ids), 2)
            rec.nilai_shu_modal = rec.amount_shu*rec.persen_shu_modal/100

            rec.nilai_shu_simpanan = rec.amount_shu*rec.persen_shu_simpanan/100
            rec.nilai_shu_pinjaman = rec.amount_shu*rec.persen_shu_pinjaman/100
            rec.nilai_shu_cadangan = rec.amount_shu*rec.persen_shu_cadangan/100
            rec.nilai_shu_pengurus = rec.amount_shu*rec.persen_shu_pengurus/100

            rec.tot_pembulatan_shu = (rec.nilai_shu_simpanan+rec.nilai_shu_pinjaman) - rec.tot_shu_dibagikan
            

    def action_get_transaksi_shu(self):
        data = []
        moveObj = self.env['res.partner']
        # movePelunasanIds = moveObj.search([]).ids
        AnggotaIds = moveObj.search([('is_anggota','=',True)])
        # anggotaObj= [self.env['res.partner'].search([('partner_id','=',partner.id)]) for partner in self ]

        # AnggotaIds = moveObj.search([('total_saldo_simpanan','>',0)])
        # self.pelunasan_detail_ids = [(4,0,movePelunasanIds)]buat Many2many
        noUrut = 0
        for a in AnggotaIds:
            tot_pinjaman = 0
            pinjamanObj= [self.env['pinjaman'].search([('partner_id','=',a.id),('date','>=',self.date_start),('date','<',self.end_date)])]
            tot_pinjaman = sum(x.jumlah_pinjaman for pinjaman in pinjamanObj for x in pinjaman)
            if (a.total_saldo_simpanan > 0) or (tot_pinjaman > 0):
                value = {
                    'partner_id' : a.id,
                    # 'amount_shu_simpanan_anggota' : 1,
                    # 'amount_shu_pinjaman_anggota' : 1
                    'amount_shu_simpanan_anggota' : a.total_saldo_simpanan,
                    'amount_shu_pinjaman_anggota' : tot_pinjaman
                
                
                }
                noUrut += 1
                data.append((0,0,value))
        self.shu_transaksi_detail_ids = data
        self.state = 'confirmed'
        self.jum_anggota = noUrut


    def action_validate(self):
        # data = []
        # moveObj = self.env['shu.transaksi.line']
        # # movePelunasanIds = moveObj.search([]).ids
        # shuIds = moveObj.search([('shu_transaksi_id','=',self.id)])
        # # # self.pelunasan_detail_ids = [(4,0,movePelunasanIds)]buat Many2many

        # jum_shu_anggota = 0

        # for a in shuIds:
        #     if self.amount_shu_simpanan > 0:
        #         jum_shu_anggota = ((a.amount_shu_simpanan_anggota / self.amount_shu_simpanan)*(self.persen_shu_modal/100) * self.amount_shu) + ((a.amount_shu_pinjaman_anggota / self.amount_shu_pinjaman)*(self.persen_shu_pinjaman/100) * self.amount_shu)
        #     else:
        #         jum_shu_anggota = 0
        #     a.write({'amount_shu_anggota': jum_shu_anggota})
            
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
        if self.tot_shu_dibagikan > 0:
            moveObj = self.env['account.move']
            account_id = self.shu_id.account_id.id
            account_debit = self.shu_id.account_id_in.id
            account_credit = self.shu_id.account_id_out.id
            journal = self.shu_id.journal_id.id
            # if self.amount > 0:
            #     saldo = self.amount
            # else:
            #     saldo = -1*self.amount
            tot_shu = self.tot_shu_dibagikan
            # tot_shu = self.amount_shu
            label = 'Pembagian SHU'
            data = []
            data.append((0,0,{
                    'account_id' : account_id,
                    # 'partner_id' : self.partner_id.id,
                    'debit' : tot_shu,
                    'credit' : 0,
                    'name' : 'Total Pembagian SHU',
                }))
            for a in self.shu_transaksi_detail_ids:
                data.append((0,0,{
                    'account_id' : a.shu_transaksi_id.shu_id.account_id_out.id,
                    'partner_id' : a.partner_id.id,
                    'debit' : 0,
                    'credit' : a.amount_shu_anggota,
                    'name' : label,
                }))
            if not self.account_move_id:
                idmove = moveObj.create({
                    'date' : fields.Date.today(),
                    'journal_id' : journal,
                    'ref' : self.name,
                    'shu_transaksi_id' : self.id,
                    'line_ids' : data,

                })
                # idmove = moveOvj.create(val)
                self.account_move_id = idmove
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
    def action_clossing_tahunan(self):
        moveObj = self.env['account.move']        
        # account_debit = self.master_pinjaman_id.account_id_out.id
        # account_credit = self.master_pinjaman_id.account_pencairan_id_out.id
        journal = self.shu_id.journal_id.id
        
        #nilai_profit_los = 0        

        # jumlah_pokok = self.jumlah_pokok
        # biaya_adm = self.biaya_adm
        # j_sosial_amount = self.j_sosial_amount
        # s_sukarela_amount = self.s_sukarela_amount
        saldo = 0
        label = ''
        data = []
        for a in range(7):
            if a == 0:
                saldo = self.amount_shu + self.nilai_shu_modal + self.nilai_shu_simpanan + self.nilai_shu_pinjaman + self.nilai_shu_cadangan + self.nilai_shu_pengurus
                label = 'Account Balik'
                account_id = self.shu_id.clossing_profit_id.id
            elif a == 1:
                saldo = self.amount_shu
                label = 'Closing Profit Loss'
                account_id = self.shu_id.clossing_profit_id.id
            elif a == 2:
                saldo = self.nilai_shu_modal
                label = 'Closing Modal'
                account_id = self.shu_id.clossing_modal_id.id
            elif a == 3:
                saldo = self.nilai_shu_simpanan
                label = 'Closing Simpanan'
                account_id = self.shu_id.clossing_simpanan_id.id
            elif a == 4:
                saldo = self.nilai_shu_pinjaman
                label = 'Closing Pinjaman'
                account_id = self.shu_id.clossing_pinjaman_id.id
            elif a == 5:
                saldo = self.nilai_shu_cadangan
                label = 'Closing Cadangan'
                account_id = self.shu_id.clossing_cadangan_id.id
            elif a == 6:
                saldo = self.tot_pembulatan_shu
                label = 'Closing Pembulatan SHU'
                account_id = self.shu_id.clossing_pembulatan_id.id
            else:
                saldo = self.nilai_shu_pengurus
                label = 'Closing Pengurus'
                account_id = self.shu_id.clossing_pengurus_id.id

            data.append((0,0,{
                    'account_id' : account_id,
                    # 'partner_id' : self.partner_id.id,
                    'debit' : saldo if a == 0 else 0,
                    'credit' : 0 if a == 0 else saldo,
                    'name' : label,
            }))
        if self.amount_shu > 0:
            idmove = moveObj.create({
                'date' : fields.Date.today(),
                'journal_id' : journal,
                'ref' : self.name,
                'pinjaman_id' : self.id,
                'line_ids' : data,
            })
            self.state = 'closed'
            # self.account_move_id = idmove.id
            # self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))

    @api.model
    def default_get(self, fields):
        res = super(ShuTransaksi, self).default_get(fields)
        moveLineObj = self.env['account.move.line']
        income = sum(moveLineObj.search([('account_id.user_type_id.id','=', 13)]).mapped('balance'))
        other_income = sum(moveLineObj.search([('account_id.user_type_id.id','=', 14)]).mapped('balance'))
        expenses = sum(moveLineObj.search([('account_id.user_type_id.id','=', 15)]).mapped('balance'))
        cost_of_revenue = sum(moveLineObj.search([('account_id.user_type_id.id','=',17 )]).mapped('balance'))
        total = abs(income + other_income - expenses - cost_of_revenue)
        res.update({'amount_shu' : total})
        return res



class ShuTransaksiLine(models.Model):
    _name = 'shu.transaksi.line'

    name = fields.Char(string='Name')
    date = fields.Date(string='Date', default=fields.Date.today(), readonly = True)
    shu_transaksi_id = fields.Many2one('shu.transaksi', readonly = True)
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True)

    amount_shu_simpanan_anggota = fields.Float(string='Simpanan Anggota')
    # , compute='_compute_total_simpanan'
    amount_shu_pinjaman_anggota = fields.Float(string='Pinjaman Anggota')
    # , compute='_compute_total_pinjaman'
    amount_shu_anggota = fields.Float(string='SHU Anggota', compute='_compute_shu_')
    # 
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done','Done'), ('cancel', 'Cancel')],
                             default='draft', readonly = True)



    @api.depends('amount_shu_anggota','amount_shu_simpanan_anggota','amount_shu_pinjaman_anggota','shu_transaksi_id.persen_shu_modal','shu_transaksi_id.persen_shu_simpanan','shu_transaksi_id.persen_shu_pinjaman','shu_transaksi_id.persen_shu_cadangan','shu_transaksi_id.amount_shu','shu_transaksi_id.amount_shu_simpanan','shu_transaksi_id.amount_shu_pinjaman')
    def _compute_shu_(self):
        for rec in self:
            shu_simp = 0
            shu_pinj = 0
            if (rec.shu_transaksi_id.amount_shu_simpanan > 0) and (rec.shu_transaksi_id.persen_shu_simpanan > 0) and (rec.shu_transaksi_id.amount_shu > 0):
                shu_simp = ((rec.amount_shu_simpanan_anggota / rec.shu_transaksi_id.amount_shu_simpanan)*(rec.shu_transaksi_id.persen_shu_simpanan/100) * rec.shu_transaksi_id.amount_shu)
            else:
                shu_simp = 0

            if (rec.shu_transaksi_id.amount_shu_pinjaman > 0) and (rec.shu_transaksi_id.persen_shu_pinjaman > 0) and (rec.shu_transaksi_id.amount_shu > 0):
                shu_pinj = ((rec.amount_shu_pinjaman_anggota / rec.shu_transaksi_id.amount_shu_pinjaman)*(rec.shu_transaksi_id.persen_shu_pinjaman/100) * rec.shu_transaksi_id.amount_shu)
            else:
                shu_pinj = 0

            rec.amount_shu_anggota = round(shu_simp + shu_pinj, 2)
            # rec.amount_shu_anggota = shu_simp + shu_pinj

            # round(5.76543, 2)


class MasterShuKomponen(models.Model):
    _name = 'master.shu.komponen'

    name = fields.Char(string='Name')
    shu_type = fields.Selection([('modal', 'Modal'), ('simpanan','Simpanan'), ('pinjaman','Pinjaman'), ('cadangan', 'Cadangan')],
                             required=True, default='cadangan')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancel')],
                             required=True, default='draft')


class AccountMoveRelate(models.Model):
    _inherit = 'account.move'

    shu_transaksi_id = fields.Many2one('shu.transaksi')
    shu_transaksi_line_id = fields.Many2one('shu.transaksi.line')
    pembayaran_angsuran_id = fields.Many2one('validasi.transaksi', string='Pembayaran angsuran id')
    pelunasan_angsuran_id = fields.Many2one('validasi.transaksi', string='Pembayaran angsuran id')

# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'

#     account_type = fields.Many2one('account.account.type', string='Type', related='account_id.type')