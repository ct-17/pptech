from openerp import models, fields, api


class add_hidden_to_public_product_categories(models.Model):
    _inherit = "product.public.category"
    hidden_to_public = fields.Boolean('Hidden to Public Users')


class ProductTemplateInheritDPWebSale(models.Model):
    _inherit = ["product.template"]

    hidden_to_public = fields.Boolean('Hidden to Public', compute='check_hidden_to_public', store=True)

    @api.depends('public_categ_ids')
    def check_hidden_to_public(self):
        for rec in self:
            rec.hidden_to_public = False
            if any(res == True for res in rec.public_categ_ids.mapped(lambda x: x.hidden_to_public)):
                rec.hidden_to_public = True
