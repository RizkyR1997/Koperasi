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


class Pinjaman(models.Model):
    _name = 'pinjaman'

    name = fields.Char(string='No Kontrak', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    date = fields.Date(string='Date Started', default=fields.Date.today(), required=True)
    master_pinjaman_id = fields.Many2one('master.pinjaman', string='Pinjaman', required=True)        
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('to_be_approve','To be approve'), ('rejected_by_approver', 'Rejected by Approver'), ('approved','Approved'), ('done','Done'), ('closed', 'Closed')],
                             readonly=True, default='draft')
    jasa_persen = fields.Float(related='master_pinjaman_id.jasa_persen',string='Jasa Total %', readonly=True)
    jasa_persen_bulan = fields.Float(related='master_pinjaman_id.jasa_persen_bulan',string='Jasa Perbulan %', readonly=True)
    
    no_anggota = fields.Char(related='partner_id.no_anggota',string='No Anggota', readonly=True)
    # nomor_anggota = fields.Char(related='partner_id.no_anggota',string='No Anggota')
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True)
    city = fields.Char(string='City', related='partner_id.city')
    salesperson_id = fields.Many2one('res.users', related='partner_id.user_id', string='Salesperson')
    # npk = fields.Char(related='partner_id.npk',string='NPK')
    no_npk = fields.Char(related='partner_id.no_npk',string='NPK', readonly=True)
    no_rekening = fields.Char(string='Nomor Rekening', readonly=True)
    nama_bank = fields.Char(string='Nama Bank', readonly=True)
    keterangan = fields.Char(related='partner_id.keterangan',string='Keterangan', readonly=True)
    # keterangan = fields.Char(related='partner_id.keterangan',string='Keterangan')
    
    #close_date = fields.Date(string='Date Closed')
    # employee_id = fields.Many2one('employee.details', string='Agent', required=True)
    # commission_rate = fields.Float(string='Commission Percentage')
    
    
    
    jumlah_pinjaman = fields.Float(string='Jumlah Pinjaman', required=True)
    jangka_waktu = fields.Integer(string='Jangka Waktu', required=True)
    biaya_adm = fields.Float(string='Biaya Adm')
    s_sukarela_persen = fields.Float(related='master_pinjaman_id.s_sukarela_persen',string='S. Sukarela %')
    j_sosial_persen = fields.Float(related='master_pinjaman_id.j_sosial_persen',string='J. Sosial %')

    s_sukarela_amount = fields.Float(string='S. Sukarela', compute='_compute_pinjaman_')    
    j_sosial_amount = fields.Float(string='J. Sosial', compute='_compute_pinjaman_')

    tgl_pencairan = fields.Date(string='Tanggal Pencairan', default=fields.Date.today(), required=True)
    tgl_selesai = fields.Date(string='Tanggal Akhir Pinjaman', readonly=True)

    tgl_angsuran_terakhir = fields.Date(string='Tanggal Angsuran Terakhir', readonly=True)

    jumlah_jasa = fields.Float(string='Jumlah Jasa', readonly=True)

    jumlah_angsuran = fields.Float(string='Jumlah Angsuran Per Bulan', readonly=True)
    jumlah_pokok = fields.Float(string='Jumlah Pokok', compute='_compute_pinjaman_')
    total_angsuran = fields.Float(string='Total Bayar Angsuran', compute='_compute_pinjaman_')
    total_kali_angsuran = fields.Integer(string='Total Kali Angsuran', compute='_compute_pinjaman_')
    sisa_pinjaman = fields.Float(string='Sisa Pinjaman', compute='_compute_pinjaman_')
    sisa_angsuran = fields.Integer(string='Sisa Angsuran', compute='_compute_pinjaman_')

    jumlah_pokok_perbulan = fields.Float(string='Angsuran Pokok', compute='_compute_pinjaman_')
    jumlah_jasa_perbulan = fields.Float(string='Angsuran Jasa', compute='_compute_pinjaman_')
    is_generate_pinjaman = fields.Boolean(string='Is Generate Pinjaman', default=False, readonly=True)

    journal_count = fields.Integer(string='Journal',default=1, readonly=True)


    #amount = fields.Float(related='policy_id.amount', string='Amount')

    
    # hide_inv_button = fields.Boolean(copy=False)
    # note_field = fields.Html(string='Comment')
    # bengkel_id = fields.Many2one('res.partner', string='Bengkel Rekanan', required=True, domain=[('is_bengkel_rekanan', '=', True)])
    # nama_asuransi = fields.Char(string='Nama Asuransi')
    # tanggal_kejadian = fields.Date(string='Tanggal Kejadian', )
    # no_polis = fields.Char(string='No Polis')
    # nopol_kendaraan = fields.Char(string='Nopol Kendaraan')
    # note = fields.Text(string='Kronologi')
    # estimation_budget_insurance_ids = fields.One2many('estimation.budget.insurance', 'insurance_id', string='Estimation Budget Insurance')
    # estimation_budget_workshop_ids = fields.One2many('estimation.budget.workshop', 'insurance_id', string='Estimation Budget Workshop')
    pinjaman_detail_ids = fields.One2many('pinjaman.details', 'pinjaman_id', string='Detail Angsuran')
    hide_inv_button = fields.Boolean(copy=False, readonly=True) 
    invoice_ids = fields.One2many('account.move', 'pinjaman_id', string='Invoices', readonly=True)
    detail_image_ids = fields.One2many('detail.image.pinjaman', 'pinjaman_id', string='Detail image')
    note_field = fields.Html(string='Note')

    def action_to_be_approve(self):
        if self.jumlah_pinjaman > 0:
            self.state = 'to_be_approve'
            # self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))

    def action_submit_confirmed(self):
        if self.jumlah_pinjaman > 0:
            self.state = 'confirmed'
            # self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))

    def action_rejected_by_approver(self):
        if self.jumlah_pinjaman > 0:
            self.state = 'rejected_by_approver'
            # self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))

    def action_approved(self):
        moveObj = self.env['account.move']
        # masterPinjaman = self.env['master.pinjaman'].search([('pinjaman_duration','=',self.jangka_waktu)])
        account_debit = self.master_pinjaman_id.account_id2.id
        account_credit = self.master_pinjaman_id.account_id_out.id
        journal = self.master_pinjaman_id.journal_id.id
        saldo = self.pinjaman_detail_ids.filtered(lambda x : x.type_pinjaman == 'outbound').saldo_pinjaman
        data = []
        for a in range(2):
            data.append((0,0,{
                'account_id' : account_debit if a == 0 else account_credit,
                'partner_id' : self.partner_id.id,
                'debit' : saldo if a == 0 else 0,
                'credit' : 0 if a == 0 else saldo,
            }))
        if self.jumlah_pinjaman > 0:
            moveObj.create({
                'date' : fields.Date.today(),
                'journal_id' : journal,
                'ref' : self.name,
                'pinjaman_id' : self.id,
                'line_ids' : data,
            })
            self.state = 'approved'
            # self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))


    def action_done(self):
        moveObj = self.env['account.move']        
        # account_debit = self.master_pinjaman_id.account_id_out.id
        # account_credit = self.master_pinjaman_id.account_pencairan_id_out.id
        journal = self.master_pinjaman_id.journal_id.id
        
        jumlah_pinjaman = self.jumlah_pinjaman

        jumlah_pokok = self.jumlah_pokok
        biaya_adm = self.biaya_adm
        j_sosial_amount = self.j_sosial_amount
        s_sukarela_amount = self.s_sukarela_amount
        saldo = 0
        label = ''
        data = []
        for a in range(5):
            if a == 0:
                saldo = jumlah_pinjaman
                label = 'Clearing Pinjaman'
                account_id = self.master_pinjaman_id.account_id_out.id
            elif a == 1:
                saldo = jumlah_pokok
                label = 'Pencairan Pinjaman Net'
                account_id = self.master_pinjaman_id.account_id.id
            elif a == 2:
                saldo = biaya_adm
                label = 'Biaya Adm'
                account_id = self.master_pinjaman_id.account_expense.id
            elif a == 3:
                saldo = j_sosial_amount
                label = 'Jaminan sosial'
                account_id = self.master_pinjaman_id.account_expense.id
            else:
                saldo = s_sukarela_amount
                label = 'Simpanan Sukarela'
                account_id = self.master_pinjaman_id.account_expense.id

            data.append((0,0,{
                    'account_id' : account_id,
                    'partner_id' : self.partner_id.id,
                    'debit' : saldo if a == 0 else 0,
                    'credit' : 0 if a == 0 else saldo,
                    'name' : label,
            }))
        if self.jumlah_pinjaman > 0:
            idmove = moveObj.create({
                'date' : fields.Date.today(),
                'journal_id' : journal,
                'ref' : self.name,
                'pinjaman_id' : self.id,
                'line_ids' : data,
            })
            self.state = 'done'
            # self.account_move_id = idmove.id
            # self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))

    def action_closed(self):
        if self.jumlah_pinjaman > 0:
            self.state = 'closed'
            # self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))


    def generate_angsuran(self):
        if self.jumlah_pinjaman > 0:
            self.state = 'draft'
            self.hide_inv_button = True
        else:
            raise UserError(_("Jumlah pinjaman harus lebih besar dari nol..."))


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


    
    @api.depends('pinjaman_detail_ids','s_sukarela_amount','j_sosial_amount','jumlah_pinjaman','jangka_waktu','s_sukarela_persen','j_sosial_persen','biaya_adm','jumlah_pokok','total_angsuran','total_kali_angsuran','jumlah_jasa')
    def _compute_pinjaman_(self):

        tot_angsur = 0

        for rec in self:
            if rec.s_sukarela_persen > 0:
                rec.s_sukarela_amount = (rec.jumlah_pinjaman * rec.s_sukarela_persen)/100
            if rec.j_sosial_persen > 0:
                rec.j_sosial_amount = (rec.jumlah_pinjaman * rec.j_sosial_persen)/100
            if rec.jangka_waktu > 0:
                rec.jumlah_angsuran = (rec.jumlah_pinjaman / rec.jangka_waktu) + (((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu)
            if rec.jangka_waktu > 0:
                rec.jumlah_jasa = (((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu)
            rec.jumlah_pokok = rec.jumlah_pinjaman - (rec.s_sukarela_amount + rec.j_sosial_amount + rec.biaya_adm)
            
            rec.sisa_angsuran = rec.jangka_waktu - rec.total_kali_angsuran
            if rec.jangka_waktu > 0:
                rec.jumlah_pokok_perbulan = rec.jumlah_pinjaman / rec.jangka_waktu
            else:
                rec.jumlah_pokok_perbulan = 0
            if rec.jangka_waktu > 0:
                rec.jumlah_jasa_perbulan = ((rec.jumlah_pinjaman*rec.jasa_persen)/100)/rec.jangka_waktu
            else:
                rec.jumlah_jasa_perbulan = 0
            

            rec.total_angsuran = sum(line.jumlah_pokok_perbulan for line in rec.pinjaman_detail_ids.filtered(lambda x: x.status=='paid'))

            rec.sisa_pinjaman = rec.jumlah_pinjaman - rec.total_angsuran

            # if line.status='paid': 

            # for line in rec.pinjaman_detail_ids:
            #     tot_angsur =+ line.jumlah_pokok_perbulan
            #     if line.status = 'paid':
            #         tot_angsur =+ line.jumlah_pokok
            # rec.total_angsuran = tot_angsur

    def action_generate_angsuran(self):
        data = []
        noUrut = 0
        saldoPinjaman = 0
        saldoPinjaman += self.jumlah_pinjaman
        for a in range(self.jangka_waktu + 1):
            tglPencairan = self.tgl_pencairan
            datePlusOneMonth = tglPencairan + relativedelta(months=noUrut)
            if noUrut > 0:
                totalSaldoPinjaman = saldoPinjaman - (self.jumlah_pokok_perbulan)
                saldoPinjaman = totalSaldoPinjaman
            value = {
                'angsuran_ke' : noUrut,
                'tgl_angsuran': datePlusOneMonth,
                'type_pinjaman': 'outbound' if noUrut == 0 else 'inbound',
                'type_pelunasan': 'cash',
                'status': 'unpaid',
                'rencana_angsuran': -abs(self.jumlah_pinjaman) if noUrut == 0 else (self.jumlah_pokok_perbulan + self.jumlah_jasa_perbulan ),
                'saldo_pinjaman': saldoPinjaman,
                'jumlah_pokok_perbulan': 0 if noUrut == 0 else (self.jumlah_pokok_perbulan),
                'jumlah_jasa_perbulan': 0 if noUrut == 0 else (self.jumlah_jasa_perbulan )
            }
            noUrut += 1
            data.append((0,0,value))
        self.pinjaman_detail_ids = data
        self.is_generate_pinjaman = True
        self.state = 'confirmed'

    def action_confirm(self):
        print("kasdbaksj")
        self.state = 'confirmed'
        moveOvj = self.env['account.move']
        for rec in self.pinjaman_detail_ids:
            val = {
                'partner_id': self.partner_id.id,
                'date': datetime.now(),
                'journal_id': 2 if rec.angsuran_ke == 0 else 1,
                'move_type': 'in_invoice' if rec.angsuran_ke == 0 else 'out_invoice',
                'pinjaman_id': self.id,
                'invoice_line_ids': [(0,0,{
                    'name': 'Pinjaman Dana' if rec.angsuran_ke == 0 else 'Angsuran Ke - %s' % (rec.angsuran_ke),
                    'quantity': 1,
                    'price_unit': rec.rencana_angsuran
                })]
            }
            moveOvj.create(val)
            



    def create_bill(self):
        created_invoice=self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_origin': self.name,
            # 'journal_id': self.master_pinjaman_id.journal_pencairan_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Pencairan Pinjaman',
                'quantity': 1,
                'price_unit': self.jumlah_pokok,
                'account_id': self.master_pinjaman_id.account_pencairan_id.id,
            })],
        })
        # self.invoice_ids = created_invoice
        # if self.policy_id.payment_type == 'fixed':
        #     self.hide_inv_button = False
        # moveObj = self.env['pinjaman.details']
        # movePelunasanIds = moveObj.search([]).ids
        # movePelunasanIds = moveObj.search([('pinjaman_id','=',self.id),('status','=','unpaid'),('type_pinjaman','=','outbound')])
        self.pinjaman_detail_ids.filtered(lambda a : a.type_pinjaman == 'outbound').write({'account_move_id' : created_invoice.id})

    # def close_insurance(self):
    #     for records in self.invoice_ids:
    #         if records.state == 'paid':
    #             raise UserError(_("All invoices must be Paid"))
    #     self.state = 'closed'
    #     self.hide_inv_button = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pinjaman') or 'New'
        return super(Pinjaman, self).create(vals)
    
    def action_submit_to_be_approve1(self):
        self.state = 'to_be_approve_2'
    def action_submit_to_be_approve1(self):
        self.state = 'to_be_approve_2'

    def action_submit_rejected_by_approver_1(self):
        self.state = 'rejected_by_approver_1'
    def action_submit_rejected_by_approver_2(self):
        self.state = 'rejected_by_approver_2'
    def action_submit_approve1(self):
        self.state = 'approved_by_1'
    def action_submit_approve2(self):
        self.state = 'approved_by_2'
    # def action_submit_confirmed(self):
    #     self.state = 'confirmed'
    def action_submit_on_progress(self):
        self.state = 'on_progress'
    def action_submit_done(self):
        self.state = 'done'
    def action_submit_close(self):
        self.state = 'close'


class AccountInvoiceRelate(models.Model):
    _inherit = 'account.move'

    pinjaman_id = fields.Many2one('pinjaman', string='Pinjaman')
    pinjaman_details_id = fields.Many2one('pinjaman.details', string='Pinjaman Details')

# class EstimationBudgetInsurance(models.Model):
#     _name = 'estimation.budget.insurance'

#     product_id = fields.Many2one('product.product', string='Product')
#     insurance_id = fields.Many2one('insurance.details', string='Insurance')
#     price_list = fields.Float(string='Price')
#     remarks = fields.Text(string='Remarks')

# class EstimationBudgetWorkshop(models.Model):
#     _name = 'estimation.budget.workshop'

#     product_id = fields.Many2one('product.product', string='Product')
#     insurance_id = fields.Many2one('insurance.details', string='Insurance')
#     price_list = fields.Float(string='Price')
#     remarks = fields.Text(string='Remarks')

class DetailImage(models.Model):
    _name = 'detail.image.pinjaman'

    name = fields.Char(string='File Name')
    image = fields.Binary(string='Image', store=False,)
    remarks = fields.Char(string='Remarks')
    mime_type = fields.Char(string='Mime Type')
    pinjaman_id = fields.Many2one('pinjaman', string='pinjaman')