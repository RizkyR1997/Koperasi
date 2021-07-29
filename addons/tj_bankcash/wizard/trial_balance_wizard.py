from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SetOpenWizard(models.TransientModel):
    _name = 'trial.balance.new.wizard'

    date_start = fields.Date(string='Start Date', required=True, )
    date_end   = fields.Date(string='End Date', default=fields.Date.today(), required=True, )
    today = fields.Date("Report Date", default=fields.Date.today)
    target_move = fields.Selection([('posted', 'All Posted Entries'), 
        ('all', 'All Entries'),
        ], string='Target Moves', required=True, default='posted', readonly=True)

    def action_open(self):
        query = """ 
            CREATE OR REPLACE VIEW trial_balance_new AS (
            SELECT  row_number() OVER () as id,
                        (SELECT aa.id FROM account_account aa WHERE aa.code = data.code) as account_id,
                        data.code as code,
                        (SELECT aa.name FROM account_account aa WHERE aa.code = data.code) as description,                        
						(SELECT aa.user_type_id FROM account_account aa WHERE aa.code = data.code) as account_type,
                        sum(data.saldo_awal) as opening,
                        sum(data.total_debet) as debit,
                        sum(data.total_credit) as credit,
                        sum(data.saldo_akhir) as balance
                FROM 
                    (SELECT (SELECT aa.code FROM account_account aa WHERE aa.id = account_id) as code,
                            0 AS saldo_awal,
                            SUM(debit) AS total_debet,
                            SUM(credit) AS total_credit,
                            (SUM(debit) - SUM(credit)) AS saldo_akhir
                    FROM account_move_line
                    WHERE company_id = 1                     
                    AND date >= '%s'
                    AND date <= '%s'
                    AND parent_state = '%s'
                    GROUP BY code
                        UNION
                            SELECT  (SELECT aa.code FROM account_account aa WHERE aa.id = account_id) as code,
                                (SUM(debit) - SUM(credit)) AS saldo_awal,
                                0 AS total_debet,
                                0 AS total_credit,
                                (SUM(debit) - SUM(credit)) AS saldo_akhir
                            FROM account_move_line
                            WHERE company_id = 1
                            AND date < '%s'
                            AND parent_state = '%s'
                            GROUP BY code
                    ) data								
                GROUP BY code
            )
           """ % (self.date_start,self.date_end,self.target_move,self.date_start,self.target_move)
        self._cr.execute(query)
        self._cr.commit()
        result = self.env.ref('tj_bankcash.trial_balance_new_action').read()[0]
        return result
        
    def action_print(self):
        # raise UserError('Under Maintenance, We will be back soon')
        self.action_open()
        print("=========button_export_pdf==========")
        self.ensure_one()
        logged_users = self.env['res.company']._company_default_get('account.account')
        if self.date_start:
            if self.date_start > self.date_end:
                raise UserError("Start date should be less than end date")
        data = {
            'ids': self.ids,
            'model': self._name,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'today': self.today,
            # 'logged_users': logged_users.name,
        }

        return self.env.ref('tj_bankcash.trial_balance_new_wizard_report_action').report_action(self, data=data)

    # def generate_xlsx_report(self):
    #     date_start = datetime.strptime(str(self.date_start), "%Y-%m-%d")
    #     date_end = datetime.strptime(str(self.date_end), "%Y-%m-%d")
    #     if date_start:
    #         if date_start > date_end:
    #             raise UserError("Start date should be less than end date")
    #     data = {
    #         'ids': self.ids,
    #         'model': self._name,
    #         'date_start': self.date_start,
    #         'date_end': self.date_end,
    #         'today': self.today,
    #     }
    #     return {
    #         'type': 'ir_actions_xlsx_download',
    #         'data': {'model': 'trial.balance.new.wizard',
    #                  'options': json.dumps(data, default=date_utils.json_default),
    #                  'output_format': 'xlsx',
    #                  'report_name': 'Trial Balance Report',
    #                  }
    #     }

    # def get_xlsx_report(self, data, response):
    #     output = io.BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     fetched_data = []
    #     account_res = []
    #     journal_res = []
    #     fetched = []
    #     account_type_id = self.env.ref('account.data_account_type_liquidity').id
    #     currency_symbol = self.env.user.company_id.currency_id.symbol
    #     if data['levels'] == 'summary':
    #         state = """ WHERE am.state = 'posted' """ if data['target_move'] == 'posted' else ''
            
            # query = """SELECT to_char(am.date, 'Month') as month_part, extract(YEAR from am.date) as year_part, sum(aml.debit) AS total_debit, sum(aml.credit) AS total_credit,
            #                      sum(aml.balance) AS total_balance FROM (SELECT am.date, am.id, am.state FROM account_move as am
            #                      LEFT JOIN account_move_line aml ON aml.move_id = am.id
            #                      LEFT JOIN account_account aa ON aa.id = aml.account_id
            #                      LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
            #                      WHERE am.date BETWEEN '""" + str(data['date_from']) + """' and '""" + str(
            #     data['date_start']) + """' AND aat.id='""" + str(account_type_id) + """' ) am
            #                                  LEFT JOIN account_move_line aml ON aml.move_id = am.id
            #                                  LEFT JOIN account_account aa ON aa.id = aml.account_id
            #                                  LEFT JOIN account_account_type aat ON aat.id = aa.user_type_id
            #                                  """ + state + """GROUP BY month_part,year_part"""
            # cr = self._cr
            # cr.execute(query)
            # fetched_data = cr.dictfetchall()

class ReportTrialBalanceNewWizard(models.AbstractModel):
    _name = "report.tj_bankcash.trial_balance_new_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['date_start']
        date_end = data['date_end']
        result = {}
        print("=============")

        docs = []
        tb_new = self.env['trial.balance.new'].search([], order='code asc')
        for record in tb_new:
            docs.append({
                'id': record.id,
                'code': record.code,
                'account': record.account_id.name,
                'type': record.account_type.name,
                'opening': record.opening,
                'debit': record.debit,
                'credit': record.credit,
                'balance': record.balance,
            })
        print("TES ==============================")
        print(docs)

        result = {
            'doc_ids': docids,
            'doc_model': data['model'],
            'docs': docs,
            'data': data,
            'date_start':date_start,
            'date_end':date_end,
        }
        return result
        