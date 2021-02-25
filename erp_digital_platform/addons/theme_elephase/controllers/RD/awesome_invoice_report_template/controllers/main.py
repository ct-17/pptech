from openerp.osv import fields, osv
from openerp import  api
from datetime import datetime
from openerp import SUPERUSER_ID
from functools import partial

class add_invoice(osv.osv):
  _inherit = "res.company"


  _columns = {
   'base_color_bg': fields.char("Base Color background", size=255,required=True),
   'base_color_fg': fields.char("Base Color Foreground", size=255,required=True),
   'text_color': fields.char("Text Color", size=255,required=True),
   'company_name_color':fields.char("Company Name Color", size=255,required=True),
   'second_color_bg':fields.char("Second color background", size=255,required=True),
   'second_color_fg':fields.char("Second color Foreground", size=255,required=True),

  }
  _defaults = {
   'base_color_bg': '#A10F2B',
   'base_color_fg':'#ffffff',
   'text_color': '#333333',
   'company_name_color':'#A10F2B',
   'second_color_bg':'#eeeeee',
   'second_color_fg':'#333333',

  }
add_invoice()


class res_company_inherit(osv.osv):
  _inherit = "res.company"
  def init(self, cr):
    res = super(res_company_inherit,self).init(cr)
    paper_obj = self.pool.get('report.paperformat')
    paper_ids=paper_obj.search(cr,SUPERUSER_ID,[('name','=','CustomA4')],limit=1)
    id=paper_obj.browse(cr, SUPERUSER_ID, paper_ids).id
    company_obj = self.pool.get('res.company')
    company_ids=company_obj.search(cr,SUPERUSER_ID,[])
    for company in company_obj.browse(cr, SUPERUSER_ID, company_ids):
        company_obj.write(cr,SUPERUSER_ID,company.id,{'paperformat_id': id})
    return True


res_company_inherit()