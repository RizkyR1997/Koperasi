from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_simpanan = fields.Boolean(string='Status Simpanan')
    is_pinjaman = fields.Boolean(string='Status Pinjaman')
    is_lain2 = fields.Boolean(string='Status Lain2')

    