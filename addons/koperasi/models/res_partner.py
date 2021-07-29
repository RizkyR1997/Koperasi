from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_anggota = fields.Boolean(string='Status Anggota')
    is_pengurus = fields.Boolean(string='Status Pengurus')
    total_simpanan = fields.Integer(string='Total Simpanan', compute='_compute_total_simpanan')
    total_saldo_simpanan = fields.Float(string='Total Saldo Simpanan', compute='_compute_total_simpanan')

    total_pinjaman = fields.Integer(string='Total Pinjaman', compute='_compute_total_simpanan')
    total_saldo_pinjaman = fields.Float(string='Total Saldo Pinjaman', compute='_compute_total_simpanan')
    rf_id = fields.Char(string='Rf Id')
    no_anggota = fields.Char(string='No Anggota')
    no_npk = fields.Char(string='NPK')
    keterangan = fields.Char(string='Keterangan')

    def _compute_total_simpanan(self):
        for a in self:
            simpananObj= self.env['simpanan'].search([('partner_id','=',a.id)])
            pinjamanObj = self.env['pinjaman'].search([('partner_id','=',a.id)])
            a.total_simpanan = len(simpananObj)
            a.total_saldo_simpanan = sum(simpananObj.mapped('saldo_akhir'))
            a.total_pinjaman = len(pinjamanObj)
            a.total_saldo_pinjaman = sum(pinjamanObj.mapped('sisa_pinjaman'))
        # a.total_saldo_simpanan = sum(x.saldo_akhir for simpanan in simpananObj for x in simpanan)
        # simpananObj = self.env['simpanan'].search([('partner_id','=',self.id)])
        # self.total_saldo_simpanan = sum(simpananObj.mapped('saldo_akhir'))
        # self.total_saldo_simpanan = sum(simpanan.saldo_akhir for simpanan in simpananObj)
        # self.total_saldo_simpanan = sum(x.saldo_akhir for x in simp for simp in simpananObj )

    def _compute_total_pinjaman(self):

        pinjamanObj = [self.env['pinjaman'].search([('partner_id','=',partner.id)]) for partner in self ]
        self.total_pinjaman = len(pinjamanObj)
        # self.total_saldo_pinjaman = sum(pinjamanObj.mapped('sisa_pinjaman'))
        self.total_saldo_pinjaman = sum(x.sisa_pinjaman for pinjaman in pinjamanObj for x in pinjaman)

    def action_view_simpanan(self):
        print("sadasasdas")

    def action_view_pinjaman(self):
        print("sadasasdas")
    