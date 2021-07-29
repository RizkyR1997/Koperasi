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


class Simpanan(models.Model):
    _name = 'simpanan'

    name = fields.Char(string='No Kontrak', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done','Done'), ('closed', 'Closed')],
                             readonly=True, default='draft')
    partner_id = fields.Many2one('res.partner', string='Anggota', required=True)
    city = fields.Char(string='City', related='partner_id.city')
    salesperson_id = fields.Many2one('res.users', related='partner_id.user_id', string='Salesperson')
    date_start = fields.Date(string='Date Started', default=fields.Date.today(), required=True)
    close_date = fields.Date(string='Date Closed', readonly=True)
    # employee_id = fields.Many2one('employee.details', string='Agent', required=True)
    # commission_rate = fields.Float(string='Commission Percentage')


    no_anggota = fields.Char(related='partner_id.no_anggota',string='No Anggota')
    no_npk = fields.Char(related='partner_id.no_npk',string='NPK')
    no_rekening = fields.Char(string='Nomor Rekening', readonly=True)
    nama_bank = fields.Char(string='Nama Bank', readonly=True)
    keterangan = fields.Char(related='partner_id.keterangan',string='Keterangan')
    
    master_simpanan_id = fields.Many2one('master.simpanan', string='Simpanan', required=True)
    bunga_persen = fields.Float(related='master_simpanan_id.amount',string='Bunga %', readonly=True)
    jangka_waktu_tarikan = fields.Integer(related='master_simpanan_id.simpanan_duration',string='Jangka Waktu Tarikan')
    
    # amount = fields.Float(string='Amount')
    #amount = fields.Float(related='policy_id.amount', string='Amount')

    
    
    # bengkel_id = fields.Many2one('res.partner', string='Bengkel Rekanan', required=True, domain=[('is_bengkel_rekanan', '=', True)])
    # nama_asuransi = fields.Char(string='Nama Asuransi')
    # tanggal_kejadian = fields.Date(string='Tanggal Kejadian', )
    # no_polis = fields.Char(string='No Polis')
    # nopol_kendaraan = fields.Char(string='Nopol Kendaraan')
    # note = fields.Text(string='Kronologi')
    # estimation_budget_insurance_ids = fields.One2many('estimation.budget.insurance', 'insurance_id', string='Estimation Budget Insurance')
    # estimation_budget_workshop_ids = fields.One2many('estimation.budget.workshop', 'insurance_id', string='Estimation Budget Workshop')
    simpanan_detail_ids = fields.One2many('simpanan.details', 'simpanan_id', string='Detail Simpanan')
    hide_inv_button = fields.Boolean(copy=False, readonly=True)    
    invoice_ids = fields.One2many('account.move', 'simpanan_id', string='Invoices', readonly=True)
    detail_image_ids = fields.One2many('detail.image.simpanan', 'simpanan_id', string='Detail image')

    note_field = fields.Html(string='Note')
    saldo_akhir = fields.Float(string='Saldo Akhir', compute='_compute_simpanan_')

    journal_count = fields.Integer(string='Journal',default=1, readonly=True)

    @api.depends('simpanan_detail_ids')
    def _compute_simpanan_(self):
        for rec in self:
            rec.saldo_akhir = sum(line.amount for line in rec.simpanan_detail_ids)

        # self.saldo_akhir = sum(line.jumlah_pokok_perbulan for line in rec.pinjaman_detail_ids.filtered(lambda x: x.status=='paid'))


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


    # def confirm_insurance(self):
    #     if self.amount > 0:
    #         self.state = 'confirmed'
    #         self.hide_inv_button = True
    #     else:
    #         raise UserError(_("Amount should be Greater than Zero"))


    # def create_invoice(self):
    #     created_invoice=self.env['account.move'].create({
    #         'move_type': 'out_invoice',
    #         'partner_id': self.partner_id.id,
    #         'invoice_user_id': self.env.user.id,
    #         'invoice_origin': self.name,
    #         'invoice_line_ids': [(0, 0, {
    #             'name': 'Invoice For Insurance',
    #             'quantity': 1,
    #             'price_unit': self.amount,
    #             'account_id': 41,
    #         })],
    #     })
    #     self.invoice_ids = created_invoice
    #     if self.policy_id.payment_type == 'fixed':
    #         self.hide_inv_button = False

    # def close_insurance(self):
    #     for records in self.invoice_ids:
    #         if records.state == 'paid':
    #             raise UserError(_("All invoices must be Paid"))
    #     self.state = 'closed'
    #     self.hide_inv_button = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('simpanan') or 'New'

        return super(Simpanan, self).create(vals)
    
    
    def action_submit_confirmed(self):
        self.state = 'confirmed'
   
    def action_submit_done(self):
        self.state = 'done'
    def action_submit_close(self):
        self.state = 'close'


class AccountInvoiceRelate(models.Model):
    _inherit = 'account.move'

    simpanan_id = fields.Many2one('simpanan', string='Simpanan')
    simpanan_details_id = fields.Many2one('simpanan.details', string='Simpanan Details')

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

class DetailImageSimpanan(models.Model):
    _name = 'detail.image.simpanan'

    name = fields.Char(string='File Name')
    image = fields.Binary(string='Image', store=True,)
    remarks = fields.Char(string='Remarks')
    mime_type = fields.Char(string='Mime Type')
    simpanan_id = fields.Many2one('simpanan', string='Simpanan')