from openerp import models, fields, api
from openerp.osv import fields as old_fields
import openerp.addons.decimal_precision as dp


class purchaseOrder(models.Model):
    _inherit = "purchase.order"

    po_num = fields.Char('Chandler PO No')
    so_num = fields.Char('Chandler SO No')
    marking_num = fields.Char('Chandler Marking No')
    estimated_departure = fields.Date('Estimated Date of Departure')
    name = fields.Char(help="")
    date_order = fields.Datetime(help="")
    # minimum_planned_date = fields.Datetime(help="")
    origin = fields.Char(help="")
    state = fields.Selection(help="")
    order_remarks = fields.Char('Remarks')
    other_vessel_name = fields.Char('Other Vessel Name')
    other_shipping_agent = fields.Char('Other Shipping Agent')
    order_mobile_number = fields.Char('Mobile Number')
    order_contact_person = fields.Char('Contact Person')
    parent_partner_id = fields.Many2one(related="dest_address_id.parent_id", string='Parent Company')

    amount_discount = fields.Float(string='Discount', digits=dp.get_precision('Account'))
    """
      ____                        _                                           
     / ___|__ _ _ __  _ __   ___ | |_   ___ _   _ _ __   ___ _ __   ___  ___  
    | |   / _` | '_ \| '_ \ / _ \| __| / __| | | | '_ \ / _ \ '__| / __|/ _ \ 
    | |__| (_| | | | | | | | (_) | |_  \__ \ |_| | |_) |  __/ | _  \__ \ (_) |
     \____\__,_|_| |_|_| |_|\___/ \__| |___/\__,_| .__/ \___|_|( ) |___/\___/ 
                                                 |_|           |/             
                             _                    
      ___ ___  _ __  _   _  | |__   __ _ ___  ___ 
     / __/ _ \| '_ \| | | | | '_ \ / _` / __|/ _ \
    | (_| (_) | |_) | |_| | | |_) | (_| \__ \  __/
     \___\___/| .__/ \__, | |_.__/ \__,_|___/\___|
              |_|    |___/                        
      __                  _   _               _                   
     / _|_   _ _ __   ___| |_(_) ___  _ __   | |__   ___ _ __ ___ 
    | |_| | | | '_ \ / __| __| |/ _ \| '_ \  | '_ \ / _ \ '__/ _ \
    |  _| |_| | | | | (__| |_| | (_) | | | | | | | |  __/ | |  __/
    |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_| |_| |_|\___|_|  \___|
    Cannot super, so copy base function here                                              
    """
    def _set_minimum_planned_date(self, cr, uid, ids, name, value, arg, context=None):
        if not value: return False
        if type(ids)!=type([]):
            ids=[ids]
        pol_obj = self.pool.get('purchase.order.line')
        for po in self.browse(cr, uid, ids, context=context):
            if po.order_line:
                pol_ids = pol_obj.search(cr, uid, [
                    ('order_id', '=', po.id), '|', ('date_planned', '=', po.minimum_planned_date), ('date_planned', '<', value)
                ], context=context)
                pol_obj.write(cr, uid, pol_ids, {'date_planned': value}, context=context)
        return True

    def _minimum_planned_date(self, cr, uid, ids, field_name, arg, context=None):
        res={}
        purchase_obj=self.browse(cr, uid, ids, context=context)
        for purchase in purchase_obj:
            res[purchase.id] = False
            if purchase.order_line:
                min_date=purchase.order_line[0].date_planned
                for line in purchase.order_line:
                    if line.state == 'cancel':
                        continue
                    if line.date_planned < min_date:
                        min_date=line.date_planned
                res[purchase.id]=min_date
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    def _get_purchase_order(self, cr, uid, ids, context=None):
        result = {}
        for order in self.browse(cr, uid, ids, context=context):
            result[order.id] = True
        return result.keys()

    _columns = {
        'minimum_planned_date': old_fields.function(_minimum_planned_date, fnct_inv=_set_minimum_planned_date,
                                                string='Expected Date', type='date', select=True, help="",
                                                store={
                                                    'purchase.order.line': (_get_order, ['date_planned'], 10),
                                                    'purchase.order': (_get_purchase_order, ['order_line'], 10),
                                                }),
    }
