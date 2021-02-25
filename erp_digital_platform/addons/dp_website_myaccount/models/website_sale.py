from openerp import api, fields, models
import pytz
from datetime import datetime
from openerp.http import request

class Order(models.Model):
	_inherit = 'sale.order'

	def _get_create_date_usertz(self):
		user_tz = self.env.user.tz or 'UTC'
		local = pytz.timezone(user_tz)
		for order in self:
			order.date_order_user = datetime.strftime(pytz.utc.localize(datetime.strptime(order.date_order,
		    "%Y-%m-%d %H:%M:%S")).astimezone(local),"%d %B %Y")

	date_order_user = fields.Char(compute='_get_create_date_usertz')

	def get_display_chandler(self):
		if self.user_id.name:
			return self.user_id.name
		elif self.pending_user_id.name:
			return self.pending_user_id.name + " (Waiting for Approval)"
		else:
			return "BUYTAXFREE Chandler"

	def compute_value_max(self, line):
		return int(line.product_tmpl_id.virtual_available + line.product_uom_qty)