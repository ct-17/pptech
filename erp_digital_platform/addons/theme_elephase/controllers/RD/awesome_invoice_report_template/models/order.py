# -*- coding: utf-8 -*-
from openerp import models, fields, api
import math
from openerp.exceptions import ValidationError

try:
    from num2words import num2words
except ImportError:
    raise ValidationError('In order to proceed, please install python module called `num2words`.\n How to install the latest version in Linux/UNIX or Windows System:\n 1. Download it from https://github. com/savoirfairelinux/num2words \n 2. Unzip the downloaded file\n 3. Change directory to the unziped `num2words` folder  and run this command: "python setup.py install"\n')

class AmountInWords(models.Model):
    _inherit=["sale.order"]

    amount_words= fields.Char('Cantidad en Letras:', help="The sale order total or quotation total amount in words is automatically generated by the system..few languages are supported currently",                             compute='_compute_num2words')
    
    @api.one
    def _compute_num2words(self):
        lastnum ,firstnum = math.modf(self.amount_total)
        lastnum = lastnum * 100
        before_float = ''
        try:
            before_float = (num2words(firstnum, lang=self.partner_id.lang) + ' ' + (self.currency_id.currency_name or '')).upper()
        except NotImplementedError:
            before_float = (num2words(firstnum, lang='en') + ' ' + (self.currency_id.currency_name or '')).upper()

        final_number = before_float
        if lastnum:
            final_number += ' con %s/100'%(int(lastnum))
        self.amount_words = final_number.upper()



