from openerp import models, fields, api


class DPInventoryIndicatorConfig(models.Model):
    _name = "dp.inventory.indicator.config"

    red_name = fields.Char("Red Indicator")
    green_name = fields.Char("Green Indicator")
    orange_name = fields.Char("Orange Indicator")

    @api.model
    def create(self, vals):
        rtn = super(DPInventoryIndicatorConfig, self).create(vals)
        rtn.update_product()
        return rtn

    @api.multi
    def write(self, vals):
        rtn = super(DPInventoryIndicatorConfig, self).write(vals)
        self.update_product()
        return rtn

    @api.model
    def update_product(self):
        if self:
            self.env['product.template'].search([('indicator_id', '=', False)]).write({'indicator_id': self.id})
        return True


class DPStockConfigSettingsConfig(models.TransientModel):
    _inherit = "stock.config.settings"

    @api.model
    def _default_red_indicator(self):
        indicator_obj = self.env['dp.inventory.indicator.config']
        indicator_id = indicator_obj.search([])
        if indicator_id.exists():
            return indicator_id.red_name
        else:
            return "No Stock"

    @api.model
    def _default_green_indicator(self):
        indicator_obj = self.env['dp.inventory.indicator.config']
        indicator_id = indicator_obj.search([])
        if indicator_id.exists():
            return indicator_id.green_name
        else:
            return "Ample Stock"

    @api.model
    def _default_orange_indicator(self):
        indicator_obj = self.env['dp.inventory.indicator.config']
        indicator_id = indicator_obj.search([])
        if indicator_id.exists():
            return indicator_id.orange_name
        else:
            return "Running Low"

    red_name = fields.Char("Red Indicator", default=_default_red_indicator, required=True)
    green_name = fields.Char("Green Indicator", default=_default_green_indicator, required=True)
    orange_name = fields.Char("Orange Indicator", default=_default_orange_indicator, required=True)

    @api.model
    def update_indicator(self, vals):
        indicator_obj = self.env['dp.inventory.indicator.config']
        indicator_id = indicator_obj.search([])
        if indicator_id.exists():
            upd_dict = {}
            if vals.get("red_name", False):
                upd_dict['red_name'] = vals.get("red_name")
            if vals.get("green_name", False):
                upd_dict['green_name'] = vals.get("green_name")
            if vals.get("orange_name", False):
                upd_dict['orange_name'] = vals.get("orange_name")
            if upd_dict:
                indicator_id.write(upd_dict)
        else:
            upd_dict = {}
            if vals.get("red_name", False):
                upd_dict['red_name'] = vals.get("red_name")
            if vals.get("green_name", False):
                upd_dict['green_name'] = vals.get("green_name")
            if vals.get("orange_name", False):
                upd_dict['orange_name'] = vals.get("orange_name")

            if upd_dict:
                indicator_obj.create(upd_dict)
        return True

    @api.multi
    def write(self, vals):
        if vals.get("red_name", False) or vals.get("green_name", False) or vals.get("orange_name", False):
            self.update_indicator(vals)
        return super(DPStockConfigSettingsConfig, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get("red_name", False) or vals.get("green_name", False) or vals.get("orange_name", False):
            self.update_indicator(vals)
        return super(DPStockConfigSettingsConfig, self).create(vals)


class DPProductIndicator(models.Model):
    _inherit = "product.template"

    indicator_id = fields.Many2one("dp.inventory.indicator.config", "Indicator")
    red_name = fields.Char(related="indicator_id.red_name")
    green_name = fields.Char(related="indicator_id.green_name")
    orange_name = fields.Char(related="indicator_id.orange_name")

    red_lower_stock_limit = fields.Float("Red Lower Stock Indicator Limit %")
    orange_lower_stock_limit = fields.Float("Orange Lower Stock Indicator Limit %")
    green_lower_stock_limit = fields.Float("Green Lower Stock Indicator Limit %")

    red_upper_stock_limit = fields.Float("Red Upper Stock Indicator Limit %")
    orange_upper_stock_limit = fields.Float("Orange Stock Upper Indicator Limit %")
    green_upper_stock_limit = fields.Float("Green Upper Stock Indicator Limit %")

    dp_minimum_qty = fields.Float("Minimum Quantity")
    dp_maximum_qty = fields.Float("Maximum Quantity")
    dp_allocated_qty = fields.Float("Allocated Quantity")

    alcohol_per = fields.Float("Alcohol %")
    origin_country_id = fields.Many2one("res.country", "Country of Origin")
    dp_volume = fields.Char("Volume")

    @api.model
    def check_indicator_status(self):
        product_ids = self.sudo().search([('indicator_id', '=', False)])
        if product_ids:
            ind_id = self.env['dp.inventory.indicator.config'].sudo().search([], limit=1)
            if ind_id:
                product_ids.sudo().write({'indicator_id': ind_id.id})
        return True

    @api.model
    def create(self, vals):
        rtn = super(DPProductIndicator, self).create(vals)
        rtn.check_indicator_status()
        return rtn

    @api.multi
    def write(self, vals):
        rtn = super(DPProductIndicator, self).write(vals)
        self.check_indicator_status()
        return rtn
