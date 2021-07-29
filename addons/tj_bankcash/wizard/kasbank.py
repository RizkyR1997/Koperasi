from odoo import fields, api, models
from datetime import datetime
import pytz
from pytz import timezone
# tj.kasbank.wizard
class tj_kasbank_wizard(models.TransientModel):
    _name = "tj.kasbank.wizard"
    _description = "Bank Cash"
    
   #  @api.multi
    def get_default_date_multi(self):
        date_time = pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))
        return date_time.strftime('%d/%m/%Y %H:%M:%S')

    name = fields.Char(string="Name")
    start_date = fields.Date('Start Date', default=datetime.now())
    end_date = fields.Date('End Date')
    journal_id = fields.Many2one('account.journal', 'Kas/Bank')
    journal = fields.Char(string="Kas/Bank")
    

   #  @api.multi
    def _execute_query(self, ids_categ=False, ids_product=False):
        where_end_date_awal = " b.date is null "
        where_start_date = " 1=1 "
        if self.start_date :
            where_start_date = " b.date >= '%s 00:00:00' "%self.start_date
            where_end_date_awal = " b.date < '%s 00:00:00' "%self.start_date
        where_end_date = " 1=1 "
        if self.end_date :
            where_end_date = " b.date <= '%s 23:59:59' "%self.end_date
        where_journal = " 1=1 "
        if self.journal_id :
            where_journal = " a.journal_id = %s "%self.journal_id.id

        query = """
            select 
            (select name from account_journal aj where aj.id=data.journal_id) as journal,
            data.* from (

            select '2018-01-01' as date,b.journal_id,0 as account_id,0 as partner_id,'' as ref,'' as note,'' as name,'' as number,sum(b.amount) as sawal,0 as penerimaan,0 as pengeluaan,0 as sakir,1 as id from account_bank_statement a left join account_bank_statement_line b on a.id=b.statement_id  where """ + where_journal + """ and  """+ where_end_date_awal +""" group by b.journal_id
                  
            UNION
            select b.date,b.journal_id,b.account_id,b.partner_id,b.ref,b.note,b.name,a.number,0 as sawal,b.amount as penerimaan,0 as pengeluaran,0 sakir,b.id from account_bank_statement a left join account_bank_statement_line b on a.id=b.statement_id  where """ + where_journal + """ and b.amount > 0
                  and """+ where_start_date +""" and """+ where_end_date +"""

            UNION
            select b.date,b.journal_id,b.account_id,b.partner_id,b.ref,b.note,b.name,a.number,0 as sawal,0 as penerimaan,-b.amount as pengeluaran,0 as sakir,b.id from account_bank_statement a left join account_bank_statement_line b on a.id=b.statement_id  where """ + where_journal + """ and b.amount < 0
                  and """+ where_start_date +""" and """+ where_end_date +"""                  
                  
                  ) data
                  order by date,number
        """
        self._cr.execute(query)
        return self._cr.dictfetchall()
        # return self._cr.fetchall()

        # select row_number() OVER () as id,b.date,b.journal_id,b.account_id,b.partner_id,b.ref,b.note,b.name,b.number,0 as sawal,0 as penerimaan,-b.amount as pengeluaran,0 as sakir from account_bank_statement a left join account_bank_statement_line b on a.id=b.statement_id  where a.journal_id=21 and b.amount < 0
        # UNION
        #     select '9999-12-31' as date,b.journal_id,0 as account_id,0 as partner_id,'' as ref,'' as note,'' as name,'' as number,0 as sawal,0 as penerimaan,0 as pengeluaran,sum(b.amount) as sakir from account_bank_statement a left join account_bank_statement_line b on a.id=b.statement_id  where """ + where_journal + """ and """+ where_end_date +"""  group by b.journal_id

        #,b.number as number2
        

   #  @api.multi
    def get_results(self):
        result = self._execute_query()
        return result

   #  @api.multi
    # def action_print(self):
        # return self.env['report'].get_action(self, 'tj_bankcash.tj_kasbank_template')

    def action_print(self):
        """Call when button 'Get Report' clicked.
        """
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.start_date,
                'date_end': self.end_date,
                'journal_id': self.journal_id,
                'record': self.get_results()
            },
        }
        return self.env.ref('tj_bankcash.record_bankcash_id').report_action(self,data=data)


class ValueReport(models.AbstractModel):
    _name = 'report.tj_bankcash.tj_kasbank_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        journal_id = data['form']['journal_id']
        record = data['form']['record']
        domain = [
                ('date_order','>=',date_start),
                ('date_order','<=',date_end)
                ]
        print("========================")
        print(record)

        return {
            'doc_ids': docids,
            'doc_model': data['model'],
            'docs': record,
            'data': data,
            'journal': journal_id,
            'date_start':date_start,
            }

 