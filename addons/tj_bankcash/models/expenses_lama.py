# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class AccountExpenses(models.Model):
    _name = 'account.expenses'
    _description = "Account Expenses"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date desc, id desc'

    name = fields.Char('Name', )
    ref = fields.Char('Reference', )
    date = fields.Date('Tanggal', )
    date_back = fields.Date('Tanggal Kembali', )
    no_mobil = fields.Char('No Mobil', )
    jenis_mobil = fields.Char('Jenis Mobil', )
    operation_type = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], string='Type',
                            readonly=False, index=True, copy=False, default='cash', track_visibility='onchange')
    partner_id = fields.Many2one("res.partner", "Partner")
    employee_id = fields.Many2one("hr.employee", "Employee")
    kenek = fields.Char("Kenek", )
    account_id = fields.Many2one("account.account", "Account")
    journal_id = fields.Many2one("account.journal", "Journal")
    # do_bkb_id = fields.Many2one("stock.picking", "No DO/BKB", store=True, index=True)
    # region_id = fields.Many2one("res.partner.region", "Region")
    # cluster_id = fields.Many2one("res.partner.cluster", "Cluster")
    # kategori1_id = fields.Many2one("res.partner.kategori1", "Kategori 1")
    # kategori2_id = fields.Many2one("res.partner.kategori2", "Kategori 2")
    # kategori3_id = fields.Many2one("res.partner.kategori3", "Kategori 3")
    # kategori4_id = fields.Many2one("res.partner.kategori4", "Kategori 4")
    # divisi1_id = fields.Many2one("res.partner.divisi1", "Divisi 1")
    # divisi2_id = fields.Many2one("res.partner.divisi2", "Divisi 2")
    # jalur_id = fields.Many2one("res.partner.jalur", "Jalur")
    # dc1_id = fields.Many2one("res.partner.dc1", "DC 1")
    # kelompok_id = fields.Many2one("res.partner.kelompok", "Kelompok")
    statement_id = fields.Many2one("account.bank.statement", "Statement")
    statement_line_id = fields.Many2one("account.bank.statement.line", "Label")
    expenses_line = fields.One2many("account.expenses.line", "order_id", string="Expenses Lines")
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancelled'), ('reconcile', 'Reconciled')],
        string='Status',
        readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    total = fields.Float('Total', compute="_compute_total", readonly=True, store=True)
    kasbon = fields.Float('Kasbon', )
    selisih = fields.Float('Selisih', )
    note = fields.Text('Note', )

    @api.onchange('statement_id')
    @api.depends('statement_id')
    def _statement_id(self):
        res = {}
        res['domain'] = {'statement_line_id': [('statement_id', '=', self.statement_id.id)]}
        return res

   #  @api.multi
    def button_journal_entries(self):
        action = self.env.ref('tj_bankcash.action_account_expenses_tree1').read()[0]
        action['domain'] = [('expenses_id', '=', self.id)]
        return action

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('account.expenses') or '/'
        return super(AccountExpenses, self).create(vals)

   #  @api.multi
    def write(self, vals):
        res = super(AccountExpenses, self).write(vals)
        if 'stop_write_recursion' not in self.env.context:
            self.my_other_logic(vals)
        return res

# get values to write
   #  @api.multi
    def my_other_logic(self, vals):
        if self.statement_line_id:
            kasbon = self.statement_line_id.amount
            selisih = self.total + self.statement_line_id.amount
            other_values = {'kasbon': kasbon,
                            'selisih': selisih}
            self.with_context(stop_write_recursion=1).write(other_values)

   #  @api.multi
    def unlink(self):
        for order in self:
            if not order.state == 'cancel':
                raise UserError(_('In order to delete a Biaya Operasional, you must cancel it first.'))
        return super(AccountExpenses, self).unlink()

   #  @api.multi
    def copy_data(self, default=None):
        if default is None:
            default = {}
            default['name'] = self.env['ir.sequence'].next_by_code('account.expenses') or '/'
        if 'expenses_line' not in default:
            default['expenses_line'] = [(0, 0, line.copy_data()[0]) for line in self.expenses_line]
        return super(AccountExpenses, self).copy_data(default)

    @api.onchange('expenses_line')
    @api.depends('expenses_line')
    def _compute_total(self):
        for rec in self:
            if rec.expenses_line:
                total = 0
                for line in rec.expenses_line:
                    total += line.quantity * line.unit_price
                rec.update({'total': total})

# print("self.type=>", self.type)credit payment                

    @api.onchange('operation_type')
    def onchange_type(self):
        if self.operation_type == 'credit':
            self.account_id = self.partner_id.property_account_payable_id.id
        else:
            self.account_id = self.partner_id.property_account_receivable_id.id

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.onchange_type()
        # if self.partner_id:
        #     self.account_id = self.partner_id.property_account_receivable_id.id
        

    # @api.onchange('do_bkb_id')
    # def onchange_do_bkb_id(self):
    #     if self.do_bkb_id:
    #         self.partner_id = self.do_bkb_id.partner_id.id or False
    #         self.region_id = self.do_bkb_id.region_id.id or False
    #         self.cluster_id = self.do_bkb_id.cluster_id.id or False
    #         self.kategori1_id = self.do_bkb_id.kategori1_id.id or False
    #         self.kategori2_id = self.do_bkb_id.kategori2_id.id or False
    #         self.kategori3_id = self.do_bkb_id.kategori3_id.id or False
    #         self.kategori4_id = self.do_bkb_id.kategori4_id.id or False
    #         self.divisi1_id = self.do_bkb_id.divisi1_id.id or False
    #         self.divisi2_id = self.do_bkb_id.divisi2_id.id or False
    #         self.jalur_id = self.do_bkb_id.jalur_id.id or False
    #         self.dc1_id = self.do_bkb_id.dc1_id.id or False
    #         self.kelompok_id = self.do_bkb_id.kelompok_id.id or False
    #     else:
    #         self.partner_id = False
    #         self.region_id = False
    #         self.cluster_id = False
    #         self.kategori1_id = False
    #         self.kategori2_id = False
    #         self.kategori3_id = False
    #         self.kategori4_id = False
    #         self.divisi1_id = False
    #         self.divisi2_id = False
    #         self.jalur_id = False
    #         self.dc1_id = False
    #         self.kelompok_id = False

   #  @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

   #  @api.multi
    def action_confirm(self):
        if len(self.expenses_line) == 0:
            raise UserError(_('In Expenses Lines not Empty!!!'))
        self.account_move_entry()
        self.write({'state': 'confirm'})

   #  @api.multi
    def action_cancel(self):
        self.account_move_delete()
        self.write({'state': 'cancel'})

   #  @api.multi
    def account_move_entry(self):
        AccountMove = self.env['account.move']
        if self.expenses_line:
            # date = self._context.get('force_period_date', fields.Date.context_today(self))
            # new_account_move = AccountMove.sudo().create({
            # new_account_move = AccountMove.create({
            #     'journal_id': self.journal_id.id,
            #     'date': date,
            #     'ref': self.name,
            #     'expenses_id': self.id,
            # })
            line_ids = []
            price = 0
            for line in self.expenses_line:
                vals_debit = (0, 0, {
                    'type': 'dest',
                    'name': line.name,
                    # 'product_id': line.product_id.id,
                    # 'quantity': line.quantity,
                    # 'product_uom_id': line.product_id.uom_id.id,
                    'ref': self.name,
                    'partner_id': self.partner_id.id,
                    'debit': line.quantity * line.unit_price,
                    'credit': 0,
                    'account_id': line.account_id.id,
                    'date_maturity': self.date,
                })
                line_ids.append(vals_debit)
                price += line.quantity * line.unit_price

            vals_credit = (0, 0, {
                'type': 'dest',
                'name': self.name,
                # 'product_id': False,
                # 'quantity': False,
                # 'product_uom_id': False,
                'ref': self.name,
                'partner_id': self.partner_id.id,
                'debit': 0,
                'credit': price,
                'account_id': self.account_id.id,
                'date_maturity': self.date,
            })

            line_ids.append(vals_credit)
            print(line_ids)
            new_account_move = AccountMove.create({
                'journal_id': self.journal_id.id,
                'date': fields.Date.context_today(self),
                'ref': self.name,
                'expenses_id': self.id,
                'line_ids': line_ids,
            })
            new_account_move.post()
            # price = 0
            # for line in self.expenses_line:
            #     vals_debit = {
            #         'move_id': new_account_move.id,
            #         'name': line.name,
            #         'product_id': line.product_id.id,
            #         'quantity': line.quantity,
            #         'product_uom_id': line.product_id.uom_id.id,
            #         'ref': self.name,
            #         'partner_id': self.partner_id.id,
            #         'debit': line.quantity * line.unit_price,
            #         'credit': 0,
            #         'account_id': line.account_id.id,
            #     }
            #     line_ids.append(vals_debit)
            #     price += line.quantity * line.unit_price
            #
            # vals_credit = {
            #     'move_id': new_account_move.id,
            #     'name': False,
            #     'product_id': False,
            #     'quantity': False,
            #     'product_uom_id': False,
            #     'ref': self.name,
            #     'partner_id': self.partner_id.id,
            #     'debit': 0,
            #     'credit': price,
            #     'account_id': self.account_id.id,
            # }
            #
            # line_ids.append(vals_credit)
            # AccountMoveLines.create(line_ids)
            # new_account_move.post()

   #  @api.multi
    def account_move_delete(self):
        move = self.env['account.move'].search([('expenses_id', '=', self.id)])
        for rec in move:
            if rec.state == 'posted':
                rec.button_cancel()
            rec.line_ids.unlink()
            rec.unlink()


class AccountExpensesLine(models.Model):
    _name = 'account.expenses.line'
    _description = 'Account Expenses Line'
    _order = 'order_id, sequence, id'

    order_id = fields.Many2one('account.expenses', string='Order Reference', index=True, required=True,
                               ondelete='cascade', track_visibility='onchange')
    date = fields.Date('Tanggal', related='order_id.date')
    date_back = fields.Date('Tanggal Kembali', related='order_id.date_back')
    sequence = fields.Integer(string='Sequence', default=10)
    no_mobil = fields.Char('No Mobil', related='order_id.no_mobil')
    jenis_mobil = fields.Char('Jenis Mobil', related='order_id.jenis_mobil')
    operation_type = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], string='Type', related='order_id.operation_type')
    partner_id = fields.Many2one("res.partner", "Partner", related='order_id.partner_id')
    kenek = fields.Char("Kenek", related='order_id.kenek')
    # do_bkb_id = fields.Many2one("stock.picking", "No DO/BKB", related='order_id.do_bkb_id')
    # divisi1_id = fields.Many2one("res.partner.divisi1", "Divisi 1", related='order_id.divisi1_id')
    # divisi2_id = fields.Many2one("res.partner.divisi2", "Divisi 2", related='order_id.divisi2_id')
    # jalur_id = fields.Many2one("res.partner.jalur", "Jalur", related='order_id.jalur_id')
    product_id = fields.Many2one("product.product", "Product")
    account_id = fields.Many2one("account.account", "Account")
    name = fields.Char('Description', )
    quantity = fields.Float('Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one("product.uom", "Uom")
    unit_price = fields.Float('Price')
    subtotal = fields.Float('Subtotal', compute="_compute_subtotal", readonly=True, store=True, digit=0)
    state = fields.Selection(related='order_id.state', store=True, readonly=False)

    note = fields.Text(related='order_id.note', store=True, readonly=False)
    statement_id = fields.Many2one("account.bank.statement", "Statement", related="order_id.statement_id")
    statement_line_id = fields.Many2one("account.bank.statement.line", "Label", related="order_id.statement_line_id")

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.account_id = self.product_id.property_account_expense_id.id
            self.name = ''
            self.product_uom = self.product_id.uom_id.id
            self.quantity = 1
            self.unit_price = 0
            self.subtotal = 0

    @api.depends('product_id', 'quantity', 'unit_price', 'subtotal')
    def _compute_subtotal(self):
        for line in self:
            subtotal = line.quantity * line.unit_price
            line.update({'subtotal': subtotal})

    # class AccountInvoice(models.Model):
    #     _inherit = 'account.invoice'
    #
    #     bop = fields.Boolean('Biaya Opr')
    #
    #     @api.onchange('do_bkb_id')
    #     def _onchange_do_bkbk_id(self):
    #         if ((self.bop) and (self.bop == True)):
    #             if self.do_bkb_id:
    #                 self.reference = self.do_bkb_id.name
    #                 self.partner_id = self.do_bkb_id.partner_id.id
    #                 self.divisi1_id = self.do_bkb_id.divisi1_id.id
    #                 self.divisi2_id = self.do_bkb_id.divisi2_id.id
    #                 self.kategori1_id = self.do_bkb_id.kategori1_id.id
    #                 self.jalur_id = self.do_bkb_id.jalur_id.id
    #             else:
    #                 self.reference = ''
    #                 self.partner_id = False
    #                 self.divisi1_id = False
    #                 self.divisi2_id = False
    #                 self.kategori1_id = False
    #                 self.jalur_id = False
    #
    #     @api.onchange('partner_id')
    #     def _onchange_partner_id(self):
    #         if ((self.bop) and (self.bop == True)):
    #             if self.partner_id:
    #                 self._journal_id()
    #                 self.account_id = self.partner_id.property_account_receivable_id.id
    #                 # self.name = 'Biaya Operasional'
    #                 if self.do_bkb_id:
    #                     self.reference = self.do_bkb_id.name
    #                     self.partner_id = self.do_bkb_id.partner_id.id
    #                     self.divisi1_id = self.do_bkb_id.divisi1_id.id
    #                     self.divisi2_id = self.do_bkb_id.divisi2_id.id
    #                     self.kategori1_id = self.do_bkb_id.kategori1_id.id
    #                     self.jalur_id = self.do_bkb_id.jalur_id.id
    #
    #     def _journal_id(self):
    #         res = {}
    #         res['domain'] = {'partner_id': [('is_sales', '=', True), ('is_spv', '=', True)]}
    #         res['domain'] = {'journal_id': [('journal_type', '=', 'cash')]}
    #         return res

    # class AccountPayment(models.Model):
    #     _inherit = 'account.payment'
    #
    #     kas_type = fields.Selection([('keluar', 'Kas Keluar Sales'),
    #                                  ('terima', 'Kas Terima Sales'),
    #                                  ('setor', 'Kas Transfer')], "Type Kas")
    #     kasbon_type = fields.Selection([('kasbon', 'Kasbon'),
    #                                     ('uang_makan', 'Uang Makan')], 'Type Kasbon')
    #     kasir_type = fields.Selection([('cash', 'Cash'), ('tf', 'Transfer')], 'Type Kasir', default='cash')
    #
    #    #  @api.multi
    #     def post(self):
    #         res = super(AccountPayment, self).post()
    #         if (self.kas_type):
    #             cr = self.env['account.bank.statement.line'].search(['|', ('id', '=', self.cash_register.id),
    #                                                                  ('expense_id', '=', self.id),
    #                                                                  ('payment_id', '=', self.id),
    #                                                                  ('partner_id', '=', self.partner_id.id)])
    #             if (self.kas_type == 'keluar'):
    #                 self.name = self.env['ir.sequence'].next_by_code('account.kas.out') or '/'
    #                 cr.write({'partner_id': self.partner_id.id,
    #                           'amount': self.amount * -1,
    #                           'expense_id': self.id,
    #                           'partner_id': self.partner_id.id,
    #                           'name': self.communication,
    #                           'ref': self.name})
    #             elif (self.kas_type == 'terima'):
    #                 self.name = self.env['ir.sequence'].next_by_code('account.kas.in') or '/'
    #                 cr.write({'partner_id': self.partner_id.id,
    #                           'amount': self.amount,
    #                           'payment_id': self.id,
    #                           'partner_id': self.partner_id.id,
    #                           'name': self.communication,
    #                           'ref': self.name})
    #             elif (self.kas_type == 'setor'):
    #                 self.name = self.env['ir.sequence'].next_by_code('account.kas.tf') or '/'
    #                 cr.write({'partner_id': self.partner_id.id,
    #                           'amount': self.amount,
    #                           'payment_id': self.id,
    #                           'partner_id': self.partner_id.id,
    #                           'name': self.communication,
    #                           'ref': self.name})
    #         return res
    #
    #     def _get_counterpart_move_line_vals(self, invoice=False):
    #         res = super(AccountPayment, self)._get_counterpart_move_line_vals(invoice=False)
    #         if (self.kas_type and self.kas_type == 'keluar' or self.kas_type == 'terima'):
    #             dobkb = ''
    #             if (self.do_bkb_id):
    #                 dobkb = ':\n' + self.do_bkb_id.name
    #             if self.payment_type == 'inbound':
    #                 res.update({'name': 'Kas Terima Sales' + dobkb})
    #             elif self.payment_type == 'outbound':
    #                 res.update({'name': 'Kas Keluar Sales' + dobkb})
    #         return res
    #
    #     @api.onchange('payment_type')
    #     def _onchange_payment_type(self):
    #         res = super(AccountPayment, self)._onchange_payment_type()
    #         if (self.kas_type):
    #             if (self.kas_type == 'keluar' or self.kas_type == 'terima'):
    #                 res['partner_type'] = 'customer'
    #                 self.partner_type = 'customer'
    #
    #         return res
    #
    #     @api.onchange('kas_type')
    #     def _onchange_kas_type(self):
    #         if self.kas_type:
    #             if (self.kas_type == 'keluar'):
    #                 self.payment_type = 'outbound'
    #                 if (self.do_bkb_id and self.kasbon_type):
    #                     self.communication = dict(self._fields['kasbon_type'].selection).get(
    #                         self.kasbon_type) + " " + self.do_bkb_id.name
    #                 if (self.do_bkb_id and self.kasir_type):
    #                     self.communication = dict(self._fields['kasir_type'].selection).get(
    #                         self.kasir_type) + " " + self.do_bkb_id.name
    #                 else:
    #                     if self.kasbon_type:
    #                         self.communication = dict(self._fields['kasbon_type'].selection).get(self.kasbon_type) + " "
    #                     if self.kasir_type:
    #                         self.communication = dict(self._fields['kasir_type'].selection).get(self.kasir_type) + " "
    #
    #             elif (self.kas_type == 'terima'):
    #                 self.payment_type = 'inbound'
    #                 if (self.do_bkb_id and self.kasbon_type):
    #                     self.communication = dict(self._fields['kasbon_type'].selection).get(
    #                         self.kasbon_type) + " " + self.do_bkb_id.name
    #                 elif (self.do_bkb_id and self.kasir_type):
    #                     self.communication = dict(self._fields['kasir_type'].selection).get(
    #                         self.kasir_type) + " " + self.do_bkb_id.name
    #                 else:
    #                     if self.kasbon_type:
    #                         self.communication = dict(self._fields['kasbon_type'].selection).get(self.kasbon_type) + " "
    #                     if self.kasir_type:
    #                         self.communication = dict(self._fields['kasir_type'].selection).get(self.kasir_type) + " "
    #
    #             elif (self.kas_type == 'setor'):
    #                 self.payment_type = 'transfer'
    #                 self.communication = False
    #                 self.do_bkb_id = False
    #                 self.divisi1_id = False
    #                 self.divisi2_id = False
    #                 self.kategori1_id = False
    #                 self.jalur_id = False
    #
    #     @api.onchange('kasbon_type')
    #     def _onchange_kasbon_type(self):
    #         if (self.kas_type and self.do_bkb_id and self.kasbon_type):
    #             self.communication = dict(self._fields['kasbon_type'].selection).get(
    #                 self.kasbon_type) + " " + self.do_bkb_id.name
    #         elif (self.kas_type and self.kasbon_type):
    #             self.communication = dict(self._fields['kasbon_type'].selection).get(self.kasbon_type) + " "
    #         elif (self.kas_type and self.kasir_type):
    #             self.communication = dict(self._fields['kasir_type'].selection).get(self.kasir_type) + " "
    #
    #     @api.onchange('do_bkb_id')
    #     def _onchange_do_bkb_id(self):
    #         if self.do_bkb_id:
    #             dobkb = self.env['stock.picking'].browse(self.do_bkb_id.id)
    #             if self.kasbon_type:
    #                 self.communication = dict(self._fields['kasbon_type'].selection).get(
    #                     self.kasbon_type) + " " + dobkb.name
    #             if self.kasir_type:
    #                 self.communication = dict(self._fields['kasir_type'].selection).get(
    #                     self.kasir_type) + " " + dobkb.name
    #             self.divisi1_id = dobkb.divisi1_id.id
    #             self.divisi2_id = dobkb.divisi2_id.id
    #             self.kategori1_id = dobkb.kategori1_id.id
    #             self.jalur_id = dobkb.jalur_id.id
    #         else:
    #             if self.kasbon_type:
    #                 self.communication = dict(self._fields['kasbon_type'].selection).get(self.kasbon_type) + " "
    #             if self.kasir_type:
    #                 self.communication = dict(self._fields['kasir_type'].selection).get(self.kasir_type) + " "
    #             self.divisi1_id = False
    #             self.divisi2_id = False
    #             self.kategori1_id = False
    #             self.jalur_id = False
    #
    #     @api.onchange('partner_id')
    #     @api.depends('partner_id')
    #     def _onchange_partner_id(self):
    #         if self.kas_type:
    #             res = {}
    #             res['domain'] = {'partner_id': ['|', ('is_sales', '=', True), ('is_spv', '=', True)]}
    #             return res

    # class AccountInvoiceRefundReason(models.Model):
    #     _inherit = "account.invoice.refund.reason"
    #
    #     out_invoice_type = fields.Selection([('retur', 'Retur'),
    #                                          ('sisa_baru', 'Sisa Baru'),
    #                                          ('kasbon', 'Kasbon'),
    #                                          ('biaya_opr', 'Biaya Operasional')],
    #                                         "Type Out/Refund Invoice", default='retur')
    #
    #
    # class AccountInvoiceRefund(models.TransientModel):
    #     _inherit = "account.invoice.refund"
    #
    #     out_invoice_type = fields.Selection([('retur', 'Retur'),
    #                                          ('sisa_baru', 'Sisa Baru'),
    #                                          ('kasbon', 'Kasbon'),
    #                                          ('biaya_opr', 'Biaya Operasional')],
    #                                         "Type Out/Refund Invoice", default='retur')
