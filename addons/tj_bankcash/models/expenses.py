# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class ExpensesHrEmployee(models.Model):
    _inherit = 'hr.employee'

    partner_id = fields.Many2one("res.partner", "Related Partner")
    is_mkt = fields.Boolean('Is MKT')
    code_mkt = fields.Char('MKT Code')
    is_mekanik = fields.Boolean('Is Mekanik')
    is_karu = fields.Boolean('Is Karu')
    is_kasie = fields.Boolean('Is Kasie')
    is_request = fields.Boolean('Is Request')

    is_op_persiapan = fields.Boolean('Is Persiapan')
    is_op_dyeing = fields.Boolean('Is OP Dyeing')
    is_op_printing = fields.Boolean('Is OP Printing')
    is_tracer = fields.Boolean('Is Tracer')
    is_profer = fields.Boolean('Is Profer')
    is_engraver = fields.Boolean('Is Engraver')
    is_designer = fields.Boolean('Is Designer')


class ExpensesAccountJournal(models.Model):
    _inherit = 'account.journal'

    set_expenses = fields.Boolean('Set Journal Kas Expenses')

class AccountExpenses(models.Model):
    _name = 'account.expenses'
    _description = "Account Expenses"
    _inherit = 'mail.thread'
    # _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date desc, id desc'

    name = fields.Char('Name', )
    ref = fields.Char('Reference', )
    date = fields.Date('Tanggal', )
    date_back = fields.Date('Tanggal Kembali', )
    no_mobil = fields.Char('No Mobil', )
    jenis_mobil = fields.Char('Jenis Mobil', )
    operation_type = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], string='Type',
                            readonly=True, index=True, copy=False, default='cash', track_visibility='onchange')
    partner_id = fields.Many2one("res.partner", "Partner")
    employee_id = fields.Many2one("hr.employee", "Employee")
    kenek = fields.Char("Kenek", )
    account_id = fields.Many2one("account.account", "Account Credit",)
    journal_id = fields.Many2one("account.journal", "Journal", domain=[('set_expenses','=',True)])
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
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancelled'), ('done', 'Done')],
        string='Status',
        readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    total = fields.Float('Total', compute="_compute_total", readonly=True, store=True)
    kasbon = fields.Float('Kasbon', )
    kembali = fields.Float('Kembali', )
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
            selisih = self.total + self.kembali + self.statement_line_id.amount
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

    # @api.onchange('operation_type')
    # def onchange_type(self):
    #     if self.operation_type == 'credit':
    #         self.account_id = self.partner_id.property_account_payable_id.id
    #     else:
    #         self.account_id = self.partner_id.property_account_receivable_id.id

    # @api.onchange('journal_id')
    # def onchange_journal(self):
    #     if self.journal_id:
    #         self.account_id = self.journal_id.default_credit_account_id.id
        

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
        cross_budget_line_obj = self.env['crossovered.budget.lines']
        for order in self:
            for line in order.expenses_line:
                budget_line_id = cross_budget_line_obj.search([
                    ('general_budget_id', '=', line.account_budget_id.id),
                    ('date_from', '<=', line.order_id.date),
                    ('date_to', '>=', line.order_id.date),
                ])
                print("\n budget_line_id", budget_line_id)
                if not budget_line_id:
                    raise UserError(
                        _("No active budget available for %s in selected date." % (line.account_budget_id.name)))
                elif len(budget_line_id) > 1:
                    raise UserError(_("There are multiple active budget found: %s." % (
                        ', '.join(budget_line.crossovered_budget_id.name for budget_line in budget_line_id))))
                elif budget_line_id.theoritical_amount < line.subtotal:
                    raise UserError(_(
                        "Over budget !\n\nbudget name: %s\nprice subtotal: %s\nresidual amount: %s." % (
                        line.account_budget_id.name, line.subtotal, budget_line_id.theoritical_amount)))
        self.write({'state': 'confirm'})

   #  @api.multi
    def action_cancel(self):
        self.account_move_delete()
        self.write({'state': 'cancel'})

   #  @api.multi
    def action_done(self):
        statement_obj = self.env['account.bank.statement']
        # statement_line_obj = self.env['account.bank.statement.line']
        if self.statement_id:
            obj_line_id = statement_obj.line_ids.create({
                'statement_id'  : self.statement_id.id,
                'name'          : 'Kembalian '+self.name,
                'partner_id'    : self.partner_id.id,
                'date'          : self.date_back,
                'ref'           : self.ref,
                'account_id'    : self.account_id.id,
                'amount'        : -1 * (self.total + self.statement_line_id.amount),
                })

            if obj_line_id:
                self.write({
                    'state'   : 'done',
                    'kembali' : -1 * (self.total + self.statement_line_id.amount), 
                    })
                if self.statement_id.state == 'confirm':
                    self.statement_id.button_draft()
                self.statement_id.check_confirm_bank()
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
                if not line.product_id.property_account_expense_id and not line.product_id.categ_id.property_account_expense_categ_id :
                    raise UserError(_("There is no expense account define for product %s and product category %s"%(line.product_id.name,line.product_id.categ_id.name)))
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
                    'account_id': line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id,
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

    #MASUK KE BUDGET BARENG DENGAN PO
    ##  @api.multi
    # def button_confirm(self):
    #     res = super(PurchaseOrderInherit, self).button_confirm()
    #     cross_budget_line = self.env['crossovered.budget.lines']
    #     for order in self:
    #         for rec in order.order_line:
    #             dt = datetime.strptime(order.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
    #             fdt = str(dt.year) + '-' + str(dt.strftime('%m'))
    #             # raise UserError(_(str(rec.product_id.name)+' date_month=>'+fdt))
    #             # print('hasil=>', fdt + ' ' + str(rec.account_budget_id.id) + ' ' + str(order.date_order))
    #             cbl = cross_budget_line.search(['|', ('date_from', 'ilike', fdt), ('date_to', 'ilike', fdt),
    #                                             ('general_budget_id', '=', rec.account_budget_id.id)])
    #             # print (cbl)
    #             if cbl:
    #                 for line in cbl:
    #                     if (order.date_order >= line.date_from) and (order.date_order <= line.date_to):
    #                         if (line.practical_po + rec.price_subtotal) > (line.planned_amount + line.additional_po):
    #                             raise UserError(_(
    #                                 'Budget Category : %s\nProduct Name : %s\nAmount : %s\n\nBudget : %s \nTotal PO: %s \nmelewati limit budget silahkan alokasikan ke yang lain!!!') % (
    #                                                 str(rec.product_id.account_budget_id.name),
    #                                                 str(rec.product_id.name),
    #                                                 'Rp. {:,.2f}'.format(rec.price_subtotal),
    #                                                 'Rp. {:,.2f}'.format(line.planned_amount),
    #                                                 'Rp. {:,.2f}'.format(line.practical_po + rec.price_subtotal)))
    #                 for line in cbl:
    #                     if (order.date_order >= line.date_from) and (order.date_order <= line.date_to):
    #                         line.write({
    #                             'practical_po': line.practical_po + rec.price_subtotal
    #                         })
    #                     else:
    #                         raise UserError(_('Budget Category : %s\nProduct Name : %s \ndiluar periode budget!!!') % (str(rec.product_id.account_budget_id.name), str(rec.product_id.name)))
    #             else:
    #                 raise UserError(_('Budget Category : %s\nProduct Name : %s \nbelum terdaftar di budget!!!') % (str(rec.product_id.account_budget_id.name), str(rec.product_id.name)))
    #             #rec.budget_id=cbl.id[0]
    #     return res

    ##  @api.multi
    # def button_draft(self):
    #     res = super(PurchaseOrderInherit, self).button_draft()
    #     cross_budget_line = self.env['crossovered.budget.lines']
    #     for order in self:
    #         for rec in order.order_line:
    #             rec.product_id.account_budget_id = rec.product_id.product_tmpl_id.account_budget_id.id or False
    #             dt = datetime.strptime(order.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
    #             fdt = str(dt.year) + '-' + str(dt.strftime('%m'))
    #             # raise UserError(_(str(rec.product_id.name)+' date_month=>'+fdt))
    #             # print('hasil=>', fdt + ' ' + str(rec.account_budget_id.id) + ' ' + str(order.date_order))
    #             cbl = cross_budget_line.search(['|', ('date_from', 'ilike', fdt), ('date_to', 'ilike', fdt),
    #                                             ('general_budget_id', '=', rec.account_budget_id.id)])
    #             # print (cbl)
    #             if cbl:
    #                 # raise UserError(_(str(cbl.ids)))
    #                 cbl.write({
    #                     'practical_po': cbl.practical_po - rec.price_subtotal
    #                 })
    #     return res


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
    partner_id = fields.Many2one("res.partner", "Partner")
     # , related='order_id.partner_id'
    kenek = fields.Char("Kenek", related='order_id.kenek')


    account_budget_id = fields.Many2one('account.budget.post', 'Budget')

    # do_bkb_id = fields.Many2one("stock.picking", "No DO/BKB", related='order_id.do_bkb_id')
    # divisi1_id = fields.Many2one("res.partner.divisi1", "Divisi 1", related='order_id.divisi1_id')
    # divisi2_id = fields.Many2one("res.partner.divisi2", "Divisi 2", related='order_id.divisi2_id')
    # jalur_id = fields.Many2one("res.partner.jalur", "Jalur", related='order_id.jalur_id')
    product_id = fields.Many2one("product.product", "Product")
    account_id = fields.Many2one("account.account", "Account Debet")
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
            self.account_id = self.product_id.categ_id.property_account_expense_categ_id.id
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

class CrossoveredBudgetLineInherit(models.Model):
    _inherit = 'crossovered.budget.lines'

   #  @api.multi
    def _get_expense_lines(self):
        for line in self :
            domain = [
                ('order_id.state','in',['confirm','done']),
                ('order_id.date', '>=', line.date_from),
                ('order_id.date', '<=', line.date_to),
                ('account_budget_id', '=', line.general_budget_id.id),
            ]
            expense_lines = self.env['account.expenses.line'].search(domain)
            line.expense_line_ids = expense_lines

    def get_practical_amount(self):
        paractical_amount = super(CrossoveredBudgetLineInherit, self).get_practical_amount()
        paractical_amount += sum(line.subtotal for line in self.expense_line_ids)
        return paractical_amount

    expense_line_ids = fields.Many2many(
        comodel_name='account.expenses.line',
        compute='_get_expense_lines',
        string='Expense Lines')
    