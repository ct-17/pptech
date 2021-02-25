from openerp import models, fields, api
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class DPSaleOrderStockAllocation(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        """
        similar check function here and dp_sale.sale_order_line.py
        if change logic here, need check both place
        no time to optimize and beautify it

        skip_check_qty comes from website adding order line, ensure not from website
        sale.action_quotations is sales > quotation (chandler action)
        sale.menu_sale_order is sales > sales orders (chandler action)
        dp_sale.dp_shipmaster_action_menu is shipmaster > request for quotation (shipmaster action)
        """
        if vals.has_key('order_line') and not self._context.get('skip_check_qty', False) and \
            self._context.get('params', {}).get('action', False) in (self.env.ref('sale.action_quotations').id, \
                                                                     self.env.ref('sale.menu_sale_order').id, \
                                                                     self.env.ref('dp_sale.dp_shipmaster_action_menu').id):
            for line in vals['order_line']:
                action, idx, update_dict = line
                if action == 0:
                    # 0 = create record in database
                    # stock alloc id does not exist, need to create and check stock
                    if update_dict.has_key('product_uom_qty'):
                        product_obj = self.env['product.product'].browse(update_dict.get('product_id', False))
                        if product_obj.product_tmpl_id.virtual_available - update_dict['product_uom_qty'] < 0:
                            raise except_orm(('Stock Problem'), 'Not Enough Stock for %s' % (product_obj.name))
                        if type(update_dict.get('product_uom_qty', False)) is int and update_dict.get('product_uom_qty', False) == 0:
                            raise except_orm(('Item Problem'), 'Please check the product "%s" have 0 quantity.\n Maybe You Want To Remove it' % (product_obj.name))
                        # create sale line stock allocation
                        stock_alloc_obj = self.env['sale.line.stock.allocation']
                        sao = stock_alloc_obj.create({'state': 'ongoing',
                                                'name': update_dict.get('name'),
                                                'product_id': update_dict.get('product_id'),
                                                'product_qty': update_dict.get('product_uom_qty')
                                                })
                        line[2].update({'stock_allocation_id': sao.id})
                elif action == 1:
                    # 1 = update
                    if update_dict.has_key('product_id'):
                        product_obj = self.env['product.product'].browse(update_dict.get('product_id', False))
                        sale_line = self.env['sale.order.line'].browse(idx)
                        if update_dict.has_key('product_uom_qty'):
                            if product_obj.product_tmpl_id.virtual_available - update_dict['product_uom_qty'] < 0:
                                raise except_orm(('Insufficient Stock'), 'Not Enough Stock for %s' % (product_obj.name))
                            if type(update_dict.get('product_uom_qty', False)) is int and update_dict.get('product_uom_qty', False) == 0:
                                raise except_orm(('Item Problem'), 'Please check the product "%s" have 0 quantity.\n Maybe You Want To Remove it' % (product_obj.name))
                        else:
                            if product_obj.product_tmpl_id.virtual_available - sale_line.product_uom_qty < 0:
                                raise except_orm(('Stock Problem'), 'Not Enough Stock for %s' % (product_obj.name))
                            if type(update_dict.get('product_uom_qty', False)) is int and update_dict.get('product_uom_qty', False) == 0:
                                raise except_orm(('Insufficient Stock'), 'Please check the product "%s" have 0 quantity.\n Maybe You Want To Remove it' % (product_obj.name))

                        if len(sale_line.stock_allocation_id) > 1:
                            # create sale line stock allocation
                            if update_dict.has_key('product_uom_qty'):
                                qty = update_dict.get('product_uom_qty')
                            else:
                                qty = sale_line.product_uom_qty
                            stock_alloc_obj = self.env['sale.line.stock.allocation']
                            sao = stock_alloc_obj.create({'state': 'ongoing',
                                                          'product_id': product_obj.id,
                                                          'name': product_obj.name,
                                                          'product_qty': qty
                                                          })
                            sale_line.write({'stock_allocation_id': sao.id})
                        else:
                            if update_dict.has_key('product_uom_qty'):
                                qty = update_dict.get('product_uom_qty')
                            else:
                                qty = sale_line.product_uom_qty
                            sale_line.stock_allocation_id.write({'state': 'ongoing',
                                                                'product_id': product_obj.id,
                                                                'name': product_obj.name,
                                                                'product_qty': qty
                                                                })
                    else:
                        # no product id means it is the same product, which already has stock allocation
                        sale_line = self.env['sale.order.line'].browse(idx)
                        if update_dict.has_key('product_uom_qty'):
                            diff_update = (update_dict['product_uom_qty'] - sale_line.product_uom_qty)
                            if sale_line.product_id.product_tmpl_id.virtual_available - diff_update < 0:
                                raise except_orm(('Insufficient Stock'), 'Not Enough Stock for %s' % (sale_line.product_id.name))
                            if type(update_dict.get('product_uom_qty', False)) is int and update_dict.get('product_uom_qty', False) == 0:
                                raise except_orm(('Item Problem'), 'Please check the product "%s" have 0 quantity.\n Maybe You Want To Remove it' % (sale_line.product_id.name))
                        # else:
                        #     if sale_line.product_id.product_tmpl_id.virtual_available - sale_line.product_uom_qty < 0:
                        #         raise except_orm(('Insufficient Stock'), 'Not Enough Stock for %s' % (sale_line.product_id.name))
                        #     if type(update_dict.get('product_uom_qty', False)) is int and update_dict.get('product_uom_qty', False) == 0:
                        #         raise except_orm(('Item Problem'), 'Please check the product "%s" have 0 quantity.\n Maybe You Want To Remove it' % (sale_line.product_id.name))
        res = super(DPSaleOrderStockAllocation, self).write(vals)
        if all(state == 'ongoing' for state in self.order_line.mapped(lambda x: x.stock_allocation_id).mapped(lambda y: y.state)):
            for line in self.order_line:
                stock_allocation_id = line.stock_allocation_id
                try:
                    max_qty = max(stock_allocation_id.order_line.mapped(lambda x:x.product_uom_qty))
                except ValueError:
                    continue
                except:
                    continue
                stock_allocation_id.product_qty = max_qty
        return res