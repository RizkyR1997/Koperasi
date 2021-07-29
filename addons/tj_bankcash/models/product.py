# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    expenses_ok = fields.Boolean('Is Expenses',)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    expenses_ok = fields.Boolean('Is Expenses', related='product_tmpl_id.expenses_ok')