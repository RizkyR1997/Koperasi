from odoo import models, fields, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class AccountRegisterPayments(models.TransientModel):
    _inherit = "account.payment.register"
        
        
    def action_create_payments(self):
        _logger.warning('='*40 + ' action_create_payment ' + '='*40)
        if self.line_ids:
            self.line_ids.move_id.pinjaman_details_id.write({'status':'paid'})
        return super(AccountRegisterPayments, self).action_create_payments()
        
