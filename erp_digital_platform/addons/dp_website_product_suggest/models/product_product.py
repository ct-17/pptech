from openerp import fields, api, models
from PIL import Image
from resizeimage import resizeimage
from openerp.tools.translate import _
from openerp.exceptions import except_orm
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


class DPWebProduct(models.Model):
    _inherit = 'product.product'
    suggest_product = fields.Many2many('product.template', string="Product (Max. 5)")


    @api.model
    def create(self, values):
        res = super(DPWebProduct, self).create(values)
        if res and res.image:
            image = res.image
            encoding = 'base64'
            image_stream = StringIO.StringIO(image.decode(encoding))
            image = Image.open(image_stream)
            filetype = image.format.upper()

            filetype = {
                'BMP': 'PNG',
            }.get(filetype, filetype)

            contain = resizeimage.resize_cover(image, [200, 175 ])
            background_stream = StringIO.StringIO()
            if contain.mode not in ["1", "L", "P", "RGB", "RGBA"] or (filetype == 'JPEG' and contain.mode == 'RGBA'):
                contain = contain.convert("RGB")
            contain.save(background_stream, filetype)
            res.image_resized = background_stream.getvalue().encode(encoding)
        return res

    @api.constrains('suggest_product')
    def _check_suggest_product_num(self):
        if len(self.suggest_product)>5:
            # self.suggest_product = self.suggest_product[:5]
            raise Warning('Maximum 5 suggest products can be chosen!')


class DPWebProductImage(models.Model):
    _inherit = 'product.template'
    image_resized = fields.Text(string='Resized Image')

    @api.multi
    def write(self, vals):
        res = super(DPWebProductImage, self).write(vals)
        if vals.get('image', False) and 'image' in vals.keys():
                image = vals['image']
                encoding = 'base64'
                image_stream = StringIO.StringIO(image.decode(encoding))
                image = Image.open(image_stream)
                filetype = image.format.upper()

                filetype = {
                    'BMP': 'PNG',
                }.get(filetype, filetype)

                contain = resizeimage.resize_cover(image, [200, 175])
                background_stream = StringIO.StringIO()
                if contain.mode not in ["1", "L", "P", "RGB", "RGBA"] or (filetype == 'JPEG' and contain.mode == 'RGBA'):
                    contain = contain.convert("RGB")
                contain.save(background_stream, filetype)
                self.image_resized = (background_stream.getvalue().encode(encoding))
        return res

