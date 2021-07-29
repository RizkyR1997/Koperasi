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

from odoo import models, fields


class MasterSimpanan(models.Model):
    _name = 'master.simpanan'

    name = fields.Char(string='Name', required=True)
    simpanan_type = fields.Many2one('master.simpanan.type', string='Simpanan Type', required=True)
    payment_type = fields.Selection([('fixed', 'Fixed'), ('installment', 'Installment')],
                                    required=True, default='fixed')
    amount = fields.Float(string='Bunga', required=True)
    simpanan_duration = fields.Integer(string='Duration in Days', required=True)
    note_field = fields.Html(string='Comment')

    account_id = fields.Many2one('account.account', string='Account Simpanan')
    journal_id = fields.Many2one('account.journal', string='Journal Simpanan')
    account_id_in = fields.Many2one('account.account', string='Account Simpanan In')
    account_id_out = fields.Many2one('account.account', string='Account Simpanan Out')

    account_id_bunga = fields.Many2one('account.account', string='Account Bunga')
    


class MasterSimpananType(models.Model):
    _name = 'master.simpanan.type'

    name = fields.Char(string='Name')
