from openerp import models, api, fields
from openerp.tools import openerp,image_colorize, image_resize_image_big
from dateutil.relativedelta import relativedelta
from datetime import datetime as dt
import logging, os, sys, base64
import datetime
from PIL import Image
from openerp import tools
import logging, os

_logger = logging.getLogger(__name__)


class StockLevelIndicatorConfig(models.Model):
    _inherit = "product.template"

    stock_level_indicator = fields.One2many('indicator.config', 'product_template_id', 'Product')

    @api.model
    def create(self, vals):
        res = super(StockLevelIndicatorConfig, self).create(vals)
        res.action_get_stock_level_indicators()
        return res

    @api.multi
    def action_get_stock_level_indicators(self):
        # button purely creates red orange green indicators for every product,
        # if there are more colors, this button is redacted
        try:
            all_product_objs = self.env['product.template'].search([], order='id')
            addons = tools.config.get('addons_path', False)
            files = []
            if addons:
                paths = addons.split(',')
                for path in paths:
                    if os.path.exists((os.path.join(path, 'dp_indicator_config', 'static', 'src', 'img'))):
                        abs_path = os.path.join(path, 'dp_indicator_config', 'static', 'src', 'img')
                        file_list = os.listdir(abs_path)
                        for file in file_list:
                            files.append(os.path.join(abs_path, file))

            for product in all_product_objs:
                try:
                    if not product.stock_level_indicator.exists():
                        if len(files) > 0:
                            for file in files:
                                img = image_colorize(open(file).read())
                                self.env['indicator.config'].create({
                                    'name': file[file.rfind('/')+1:-4],
                                    'img': image_resize_image_big(img.encode('base64')),
                                    'lower': 0,
                                    'upper': 0,
                                    'product_template_id': product.id
                               })
                except Exception as e:
                    _logger.error('{e}'.format(e=e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                    _logger.error('Product: ' + str(product))
                    try:
                        _logger.error('Error in {file}: '.format(file=str(file)))
                    except:
                        pass
                    _logger.error('Error in all_product_objs for loop')

                    continue
        except Exception as e:
            _logger.error('{e}'.format(e=e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('Error in action_get_stock_level_indicators')