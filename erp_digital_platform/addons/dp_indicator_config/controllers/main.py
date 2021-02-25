import logging, sys, os, base64
from openerp import tools, http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.exceptions import except_orm

from datetime import datetime as dt
from multiprocessing import cpu_count
import threading
CPU = min(cpu_count(), 16)
import json
_logger = logging.getLogger('DPwebsite_sale')


class DPwebsite_sale_product_icon(website_sale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        res = super(DPwebsite_sale_product_icon, self).product(product, category, search, **kwargs)
        # logic to show red/orange/green color on product page in website
        try:
            stock_indicator_obj = filter(lambda x: x.lower <= min((product.virtual_available / (product.dp_maximum_qty or 1) * 100), 100) <= x.upper,
                                         product.stock_level_indicator)
        except:
            stock_indicator_obj = None

        if stock_indicator_obj is not None:
            try:
                assert len(stock_indicator_obj) == 1
                res.qcontext.update({'return_image': stock_indicator_obj[0].name})
            except Exception as e:
                res.qcontext.update({'return_image': 'RED'})

                _logger.error('{e}'.format(e=e))
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('{stock_indicator_obj}: ' + str(stock_indicator_obj))
                _logger.error('Error in retrieving stock_indicator_obj')
        else:
            _, _, exc_tb = sys.exc_info()
            _logger.error('DP Maximum Quantity is {}, it must not be 0'.format(product.dp_maximum_qty))
            _logger.error('DP Allocated Quantity is {}'.format(product.dp_allocated_qty))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))

        return res