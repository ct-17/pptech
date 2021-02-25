from openerp import models, fields, api


class DPOrderNegotiationWizard(models.TransientModel):
    _name = "dp.order.negotiation.wizard"

    sale_id = fields.Many2one("sale.order", "Order")
    note = fields.Text("Remarks")
    line_ids = fields.One2many("dp.order.line.negotiation.wizard", "dp_wiz_id", "Ordered Items")
    new_line_ids = fields.One2many("dp.order.line.negotiation.wizard", "dp_wiz_id", "Additional Items")

    @api.model
    def default_get(self, fields):
        rtn = super(DPOrderNegotiationWizard, self).default_get(fields)
        if self._context.get("sale_id", False):
            sale_obj = self.env['sale.order']
            sale_id = sale_obj.browse(self._context.get("sale_id"))
            rtn['sale_id'] = sale_id.id
            lines = []
            for line in sale_id.order_line:
                lines.append([0, 0, {'product_id': line.product_id.id, 'name': line.name, 'qty': line.product_uom_qty,
                                     'unit_price': line.price_unit, 'sub_total':line.price_subtotal,
                                     'uom_id': line.product_uom.id, 'order_line_id': line.id}])
            if lines:
                rtn['line_ids'] = lines
        return rtn

    @api.multi
    def save_and_send(self):
        return True


class DPOrderLineNegotiationWizard(models.TransientModel):
    _name = "dp.order.line.negotiation.wizard"

    product_id = fields.Many2one("product.product", string="Product")
    dp_wiz_id = fields.Many2one("dp.order.negotiation.wizard", "DP Wizard")
    name = fields.Text("Product")
    qty = fields.Float("Quantity")
    uom_id = fields.Many2one("product.uom", "UOM")
    unit_price = fields.Float("Unit Price")
    sub_total = fields.Float("Subtotal")
    order_line_id = fields.Many2one("sale.order.line", "Order Line")

    @api.onchange('qty', 'unit_price')
    def onchange_total_price(self):
        self.sub_total = self.qty * self.unit_price

    @api.onchange("product_id")
    def onchange_product_id(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id
