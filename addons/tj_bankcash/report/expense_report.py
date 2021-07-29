# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class SaleReport(models.Model):
    _name = "account.expenses.report"
    _description = "Biaya Operasional Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    id = fields.Many2one('account.expenses', 'Expenses #', readonly=True)
    name = fields.Char('Reference', readonly=True)
    date = fields.Date('Tanggal', readonly=True)
    date_back = fields.Date('Tanggal Kembali', readonly=True)
    no_mobil = fields.Char('No Mobil', readonly=True)
    jenis_mobil = fields.Char('Jenis Mobil', readonly=True)
    operation_type = fields.Selection([('cash', 'Cash'), ('credit', 'Credit')], string='Type',
                            readonly=True, index=True, copy=False, default='cash', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    kenek = fields.Char('Kenek', readonly=True)
    account_id = fields.Many2one("account.account", "Account")
    journal_id = fields.Many2one("account.journal", "Journal")
    create_uid = fields.Many2one('res.users', 'Create By', readonly=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancelled'), ('reconcile', 'Reconciled')],
        string='Status',
        readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    # do_bkb_id = fields.Many2one("stock.picking", "No DO/BKB", readonly=True)
    # jalur_id = fields.Many2one("res.partner.jalur", "Jalur", readonly=True)
    statement_id = fields.Many2one("account.bank.statement", "Statement", readonly=True)
    statement_line_id = fields.Many2one("account.bank.statement.line", "Label", readonly=True)
    account_detail_id = fields.Many2one("account.account", "Account", readonly=True)
    product_id = fields.Many2one("product.product", "Product", readonly=True)
    quantity = fields.Float('Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one("product.uom", "Uom")
    unit_price = fields.Float('Price', readonly=True, store=True, digit=0)
    subtotal = fields.Float('Subtotal', readonly=True, store=True, digit=0)
    total = fields.Float('Total', readonly=True, store=True, digit=0)
    kasbon = fields.Float('Kasbon', readonly=True, store=True, digit=0)
    selisih = fields.Float('Selisih', readonly=True, store=True, digit=0)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            ae.id as id,
            ae.name as name,
            ae.date as date,
            ae.date_back as date_back,
            ae.no_mobil as no_mobil,
            ae.jenis_mobil as jenis_mobil,
            ae.operation_type as operation_type,
            ae.partner_id as partner_id,
            ae.account_id as account_id,
            ae.journal_id as journal_id,
            ae.create_uid as create_uid,
            ae.state as state,
            ae.statement_id as statement_id,
            ae.statement_line_id as statement_line_id,
            ael.account_id as account_detail_id,
            ael.product_id as product_id,
            ael.quantity as quantity,
            ael.product_uom as product_uom,
            ael.unit_price as unit_price,
            ael.subtotal as subtotal,
            ae.total as total,
            ae.kasbon as kasbon,
            ae.selisih as selisih
        """

        for field in fields.values():
            select_ += field

        from_ = """
                account_expenses ae
                    join account_expenses_line ael on (ael.order_id=ae.id)
                %s
        """ % from_clause

        groupby_ = """
            ae.id,
            ae.name,
            ae.date,
            ae.date_back,
            ae.partner_id,
            ae.create_uid,
            ae.state,
            ae.statement_id,
            ae.statement_line_id,
            ael.account_id,
            ael.product_id,
            ael.quantity,
            ael.product_uom,
            ael.unit_price,
            ael.subtotal,
            ae.total,
            ae.kasbon,
            ae.selisih %s
        """ % (groupby)

        return '%s (SELECT %s FROM %s WHERE ael.product_id IS NOT NULL GROUP BY %s)' % (with_, select_, from_, groupby_)

    @api.model_cr
    def init(self):
        # self._table = expenses_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))
