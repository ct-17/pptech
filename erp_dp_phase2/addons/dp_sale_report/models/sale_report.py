from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from openerp import tools


class INITDPSaleReportExtend(models.Model):
    _inherit = "sale.report"

    state = fields.Selection(selection_add=[("progress", "Processed"), ("shipmaster_confirm", "Order Confirmed")])
    order = fields.Char('Order Number')
    def _select(self):
        select_str = """
 
             SELECT min(s.id) as id,
                    sum(s.amount_total ) as price_total,
                    count(*) as nbr,
                    s.date_order as date,
                    s.date_confirm as date_confirm,
                    s.partner_id as partner_id,
                    s.user_id as user_id,
                    s.company_id as company_id,
                    extract(epoch from avg(date_trunc('day',s.date_confirm)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    s.state,
                    s.pricelist_id as pricelist_id,
                    s.project_id as analytic_account_id,
                    s.section_id as section_id,
                    s.name as order,
                    null as product_id,
                    null as product_uom_qty
                    
        """
        return select_str

    def _group_by(self):
        group_by_str = """
            GROUP BY  
                    s.id,
                    s.date_order,
                    s.date_confirm,
                    s.partner_id,
                    s.user_id,
                    s.company_id,
                    s.state,
                    s.pricelist_id,
                    s.project_id,
                    s.section_id,
                    s.name,
                    product_id,
                    product_uom_qty
        """
        return group_by_str

    def _from(self):
        from_str = """ sale_order s """
        return from_str

    def init(self, cr):
        # self._table = sale_report
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            %s
            FROM  %s 
            %s
            )""" % (self._table, self._select(), self._from(), self._group_by()))
