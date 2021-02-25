from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _
_state = [('draft', 'Draft'),('ongoing', 'Ongoing'),('done', 'Done'),('cancel', 'Cancelled')]


class DPSaleStockAllocation(models.Model):
    _name = "sale.line.stock.allocation"

    """
    state = draft when SO is in Enquiry
    
    Stock lock when sm add to cart, pending quotation. 
    stock is release when quote is cancel or expired or there is release of stock when chandler or sm release the line item fron the quote.
    
    """
    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', 'Product')
    product_qty = fields.Float('Product Quantity')
    state = fields.Selection(_state, 'State', default='draft')
    order_line = fields.One2many('sale.order.line', 'stock_allocation_id', 'Order Lines')