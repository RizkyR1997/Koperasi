# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (odoo@cybrosys.com)
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

{
    'name': 'Koperasi Management',
    'version': '14.0.1.0.0',
    'summary': """Koperasi Management & Operations""",
    'description': """Koperasi Management""",
    'author': 'Wibicon Techno Solutions',
    'company': 'Wibicon Techno Solutions',
    'website': 'https://www.wibicon.com',
    'category': 'Accounting',
    'depends': ['base', 'account'],
    'license': 'AGPL-3',
    'data': [
        'views/koperasi_sequence.xml',
        'views/pinjaman.xml',
        'views/pinjaman_details.xml',
        'views/simpanan.xml',
        'views/simpanan_details.xml',
        'views/master_simpanan.xml',
        'views/master_shu.xml',
        'views/master_pinjaman.xml',
        'views/koperasi_management.xml',
        'views/res_partner.xml',
        'views/validasi_transaksi.xml',
        'views/pinjaman_pelunasan.xml',
        'views/pinjaman_tunggakan.xml',
        'views/simpanan_bunga.xml',        

        'security/ir.group.xml',
        'security/ir.model.access.csv',

        'report/pinjaman.xml',
        'report/pinjaman_details.xml',
        'report/pinjaman_pelunasan.xml',
        'report/pinjaman_tunggakan.xml',
        'report/simpanan.xml',
        'report/simpanan_details.xml',
        'report/simpanan_bunga.xml',
        'report/shu.xml',
        'report/validasi_transaksi.xml',
        'report/master_pinjaman_pelunasan.xml',
        'report/master_shu.xml',
        'report/template_print.xml',
        
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

