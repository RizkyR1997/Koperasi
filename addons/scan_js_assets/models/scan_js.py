import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, exceptions, _, SUPERUSER_ID

class ResPartnerJS(models.AbstractModel):
    _inherit = "res.partner"

    @api.model
    def partner_scan_js(self, barcode):
        """ Receive a barcode scanned from the Kiosk Mode and change the attendances of corresponding partner.
            Returns either an action or a warning.
        """
        partner = self.sudo().search([('no_anggota', '=', barcode)], limit=1)
        if partner:
            # return partner._partner_action('scan_js_assets.action_scan_js')
            return partner._attendance_action('scan_js_assets.action_scan_js')
            # raise exceptions.UserError(_('harusnya ganti view'))
        return {'warning': _("No employee corresponding to Badge ID '%(no_anggota)s.'") % {'no_anggota': barcode}}

    def _attendance_action(self, next_action):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """

        self.ensure_one()
        employee = self.sudo()
        action_message = self.env["ir.actions.actions"]._for_xml_id("scan_js_assets.after_scan_js")
        return {'action': action_message}