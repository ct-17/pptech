import logging, sys
import werkzeug
from datetime import datetime
from openerp.exceptions import ValidationError
from openerp import tools, http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website_sale.controllers.main import table_compute
from openerp.exceptions import except_orm
from openerp.addons.website.models.website import slug
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF

from datetime import datetime as dt
from multiprocessing import cpu_count
import threading
CPU = min(cpu_count(), 16)
import json
_logger = logging.getLogger('DPwebsite_sale')

PPG = 21 # Products Per Page
PPR = 3  # Products Per Row


class DPwebsite_sale(website_sale):

    # def checkout_values(self, data=None):
    #     res = super(DPwebsite_sale, self).checkout_values(data)
    #     # check if confirm has been pressed
    #     confirm = False
    #     if not res.get('rec_cache', False):
    #         res['rec_cache'] = {'rec_chan_name1': request.session.get('rec_chan_name1', None),
    #                             'rec_chan_email1': request.session.get('rec_chan_email1', None),
    #                             'rec_chan_name2': request.session.get('rec_chan_name2', None),
    #                             'rec_chan_email2': request.session.get('rec_chan_email2', None),
    #                             'rec_chan_name3': request.session.get('rec_chan_name3', None),
    #                             'rec_chan_email3': request.session.get('rec_chan_email3', None),
    #                             }
    #
    #     # chandlers_obj = request.env['res.partner'].sudo().search([('supplier', '=', True)])
    #     chandlers_obj = request.env['dp.chandler.temp'].sudo().search([('active', '=', True)])
    #     vessel_obj = request.env['vessel.type'].search([])
    #     vessel_name_obj = request.env['vessel.name'].search([])
    #     shipping_obj = request.env['shipping.agent'].sudo().search([('active', '=', True)], order='name')
    #     port_obj = request.env['custom.port'].sudo().search([])
    #     user_id = request.env['res.users'].sudo().browse(request.uid)
    #     preferred_chandlers_obj = user_id.partner_id.sudo().chandler_list_for_shipmaster
    #     if res.has_key('checkout'):
    #         i = 1
    #         for pref_chan in preferred_chandlers_obj:
    #             pref_chan_id = request.env['dp.chandler.temp'].sudo().search([('partner_id', '=', pref_chan.chandler_id.id),('state', '=', 'approved')]) or request.env['dp.chandler.temp']
    #             res['checkout']['pref_chan%d' %i] = pref_chan.chandler_id.name
    #             res['checkout']['pref_chan%d_id' %i] = pref_chan_id.id
    #             i += 1
    #         res['checkout']['vessel_name'] = user_id.partner_id.vessel_name or None
    #         res['checkout']['vessel_type'] = user_id.partner_id.vessel_type or None
    #         res['checkout']['imo_number'] = user_id.partner_id.imo_number or None
    #         res['checkout']['call_sign'] = user_id.partner_id.call_sign or None
    #
    #         sale_id = ''
    #         if request.session.has_key('sale_order_id') or request.session.has_key('sale_last_order_id'):
    #             sale_id = request.session.get('sale_order_id', False)
    #         if sale_id == '' or sale_id is False:
    #             sale_id = request.session.get('sale_last_order_id', False)
    #         if sale_id == '' or sale_id is False:
    #             raise except_orm(_('Unable to retrieve sale id'), _('Please contact system admin regarding this issue!'))
    #
    #         sale_obj = request.env['sale.order'].sudo().browse(sale_id)
    #         res['checkout']['date_order'] = dt.strptime(sale_obj.date_order, DSDF).strftime('%d/%m/%Y')
    #         if sale_obj.estimated_arrival and sale_obj.shipping_agent_id:
    #             draft_date = datetime.strptime(sale_obj.estimated_arrival, '%Y-%m-%d')
    #             res['checkout']['estimated_arrival'] = draft_date.strftime("%d/%m/%Y")
    #             res['checkout']['shipping_agent_id'] = sale_obj.shipping_agent_id
    #         if sale_obj.next_port_id:
    #             res['checkout']['next_port_id'] = sale_obj.next_port_id
    #         if sale_obj.last_port_id:
    #             res['checkout']['last_port_id'] = sale_obj.last_port_id
    #
    #         seq = 1
    #         for chan in sale_obj.many_chandler:
    #             if chan.chandler.state == 'draft':
    #                 res['checkout']['rec_chan_name{}'.format(str(seq))] = chan.chandler.name
    #                 res['checkout']['rec_chan_email{}'.format(str(seq))] = chan.chandler.email
    #                 seq += 1
    #
    #         for seq in range(1,4):
    #             if not res['checkout'].has_key('rec_chan_name{}'.format(str(seq))):
    #                 res['checkout']['rec_chan_name{}'.format(str(seq))] = ''
    #                 res['checkout']['rec_chan_email{}'.format(str(seq))] = ''
    #
    #         if data:
    #             res['checkout']['estimated_arrival'] = data.get('estimated_arrival', "")
    #             res['checkout']['last_port_id'] = data.get('last_port_id', "")
    #             res['checkout']['next_port_id'] = data.get('next_port_id', "")
    #             res['checkout']['stay_duration'] = data.get('stay_duration', "")
    #             res['checkout']['vessel_id'] = data.get('vessel_id', False)
    #             res['checkout']['vessel_name'] = data.get('vessel_name', "")
    #             res['checkout']['call_sign'] = data.get('call_sign', "")
    #             res['checkout']['imo_number'] = data.get('imo_number', "")
    #             if data.get('shipping_agent_id', False):
    #                 try:
    #                     ship_ag_id = int(data.get('shipping_agent_id'))
    #                     res['checkout']['shipping_agent_id'] = request.env['shipping.agent'].sudo().search([('id', '=', ship_ag_id)])
    #                 except ValueError:
    #                     res['checkout']['shipping_agent_id'] = ''
    #             else:
    #                 res['checkout']['shipping_agent_id'] = False
    #             res['checkout']['create_vessel_name'] = data.get('create_vessel_name', "")
    #             res['checkout']['create_imo_number'] = data.get('create_imo_number', "")
    #             res['checkout']['create_vessel_id'] = data.get('create_vessel_id', False)
    #             res['checkout']['create_vessel_nrt'] = data.get('create_vessel_nrt', "")
    #             res['checkout']['create_vessel_flag'] = data.get('create_vessel_flag', "")
    #             res['checkout']['create_vessel_crew'] = data.get('create_vessel_crew', "")
    #             # res['checkout']['create_shipping_agent_id'] = data.get('create_shipping_agent_id', False)
    #             res['checkout']['submit_btn1_count'] = '0'
    #             res['checkout']['submit_btn2_count'] = '0'
    #             res['checkout']['submit_btn3_count'] = '0'
    #             res['checkout']['vessel_type'] = data.get('vessel_type', False)
    #             # res['checkout']['rec_chan_name1'] = data.get('recommend_chandler_name1', '')
    #             # res['checkout']['rec_chan_email1'] = data.get('recommend_chandler_email1', '')
    #             # res['checkout']['rec_chan_name2'] = data.get('recommend_chandler_name2', '')
    #             # res['checkout']['rec_chan_email2'] = data.get('recommend_chandler_email2', '')
    #             # res['checkout']['rec_chan_name3'] = data.get('recommend_chandler_name3', '')
    #             # res['checkout']['rec_chan_email3'] = data.get('recommend_chandler_email3', '')
    #
    #     else:
    #         for i in range(1,4):
    #             res['checkout']['pref_chan%d' % i] = "Chandler #{}".format(i)
    #             res['checkout']['pref_chan%d_id' %i] = "{}".format(None)
    #     res['chandlers1'] = chandlers_obj
    #     res['chandlers2'] = chandlers_obj
    #     res['chandlers3'] = chandlers_obj
    #     res['vessel_name_obj'] = vessel_name_obj
    #     res['vessel_obj'] = vessel_obj
    #     res['shipping_obj'] = shipping_obj
    #     res['next_port_obj'] = port_obj
    #     res['last_port_obj'] = port_obj
    #
    #     if data:
    #         # data is not None when user click confirm on /shop/checkout
    #         """ SAMPLE
    #         data =
    #         {
    #          'chandler_autocomplete_input1': u'chandler1', 'chandler_checkbox1_name': u'on',
    #          'chandler_autocomplete_input2': u'chandler3', 'chandler_checkbox2_name': u'on',
    #          'chandler_autocomplete_input3': u'chandler4', 'chandler_checkbox3_name': u'on',
    #
    #          'recommend_chandler_email1': u'chinsheng.soh@pptech.com.sg', 'recommend_chandler_name1': u'cs3',
    #          'recommend_chandler_email2': u'chinsheng.soh@pptech.com.sg', 'recommend_chandler_name2': u'cs4',
    #          'recommend_chandler_email3': u'chinsheng.soh@pptech.com.sg', 'recommend_chandler_name3': u'cs5',
    #
    #          'last_port': u'', 'next_port': u'',
    #          'name': u'shipmaster', 'phone': u'shipmastrer41@pptech.com.sg',
    #          'email': u'shipmastrer41@pptech.com.sg',
    #          'estimated_arrival': u'', 'stay_duration': u'2',
    #          'street': u'1234567', 'street2': u'callsign', 'zip': u'ship'
    #
    #          'vessel_id': u'1',
    #
    #          'shipping_agent_name': u'', 'shipping_agent_cr_number': u'', 'shipping_agent_contact': u'',
    #          'shipping_id': u'0', 'shipping_agent_id': u'',
    #
    #          }
    #
    #         """
    #         confirm = bool(data.get('check_confirm_before_cache', False))
    #         request.session.update({'rec_chan_name1': data.get('recommend_chandler_name1', None)})
    #         request.session.update({'rec_chan_email1': data.get('recommend_chandler_email1', None)})
    #         request.session.update({'rec_chan_name2': data.get('recommend_chandler_name2', None)})
    #         request.session.update({'rec_chan_email2': data.get('recommend_chandler_email2', None)})
    #         request.session.update({'rec_chan_name3': data.get('recommend_chandler_name3', None)})
    #         request.session.update({'rec_chan_email3': data.get('recommend_chandler_email3', None)})
    #         sale_id = request.session.get('sale_order_id', False)
    #         if not sale_id:
    #             sale_id = request.session.get('sale_last_order_id', False)
    #         if not sale_id:
    #             raise except_orm(_('Unable to retrieve sale order id'), _('Please contact system administrator!'))
    #         sale_order = request.env['sale.order'].browse(sale_id)
    #         vessel_name = request.env["vessel.name"].search([("name", "=", data.get('vessel_name', None))])[0].id
    #         vessel_type = request.env["vessel.type"].search([("name", "=", data.get('vessel_type', None))])[0].id
    #         order_data = {
    #             'last_port_id': data.get('last_port_id', None),
    #             'next_port_id': data.get('next_port_id', None),
    #             'stay_duration': data.get('stay_duration', None),
    #             'vessel_id': vessel_type,
    #             'vessel_name': vessel_name,
    #             "call_sign":data.get("call_sign",None),
    #             "imo_number":data.get("imo_number",None)
    #         }
    #         try:
    #             eta = dt.strptime(data.get('estimated_arrival', ), '%d/%m/%Y') if data.get('estimated_arrival', "") else False
    #         except:
    #             eta = None
    #         order_data.update({'estimated_arrival': eta})
    #
    #         last_port, next_port = None, None
    #         if data.get('last_port_id', False):
    #             port_code, port_name = data.get('last_port_id').split(':')
    #             last_port = request.env['custom.port'].sudo().search([('code', '=', port_code), ('name', '=', port_name[1:])]).id or False
    #
    #         if data.get('next_port_id', False):
    #             port_code, port_name = data.get('next_port_id').split(':')
    #             next_port = request.env['custom.port'].sudo().search([('code', '=', port_code), ('name', '=', port_name[1:])]).id or False
    #         order_data.update({
    #             'last_port_id': last_port,
    #             'next_port_id': next_port,
    #         })
    #
    #         skip_create_ship_agent = False
    #         if confirm:
    #             if data.get('shipping_agent_id', False) == 'CREATE..' and \
    #                 data.get('shipping_agent_name_cache', False) == data.get('shipping_agent_name', False) and \
    #                 data.get('shipping_agent_cr_num_cache', False) == data.get('shipping_agent_cr_number', False) and \
    #                 data.get('shipping_agent_contact_cache', False) == data.get('shipping_agent_contact', False):
    #                 skip_create_ship_agent = True
    #         if data.get('shipping_agent_id', False) == 'CREATE..':
    #             # create new shipping agent
    #             contact = data.get('shipping_agent_contact', False)
    #             cr_num = data.get('shipping_agent_cr_number', False)
    #             name = data.get('shipping_agent_name', False)
    #             try:
    #                 if contact and cr_num and name:
    #                     name = name.upper()
    #                     ship_agent_env = request.env['shipping.agent']
    #
    #                     existing = ship_agent_env.search([('name', '=', name), ('crNum', '=', cr_num), ('contact', '=', contact)])
    #                     if not existing.exists():
    #                         new_ship_agent = ship_agent_env.sudo().create({'name': name, 'crNum': cr_num,
    #                                                                         'contact': contact, 'active': True})
    #                     else:
    #                         new_ship_agent = existing
    #                 else:
    #                     _logger.error('unable to create shipping agent!!')
    #                     raise Exception
    #
    #                 if new_ship_agent.exists():
    #                     order_data.update({'shipping_agent_id': new_ship_agent.id})
    #                     new_shipping_agent_id = request.env['shipping.agent'].search([('name', '=', name.upper())])
    #                     res['checkout']['shipping_agent_id'] =  new_shipping_agent_id
    #                 else:
    #                     _logger.error('new_ship_agent does not exist!!')
    #                     raise Exception
    #
    #             except Exception as e:
    #                 exc_type, exc_obj, exc_tb = sys.exc_info()
    #                 _logger.error('Exception Type: ' + str(exc_type))
    #                 _logger.error('Exception Error Description: ' + str(exc_obj))
    #                 _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
    #                 _logger.error('unable to create new shipping agent!')
    #
    #         else:
    #             order_data.update({'shipping_agent_id': data.get('shipping_agent_id', False)})
    #
    #         skip_create_vessel = False
    #         # if confirm:
    #         #     if data.get('vessel_name', False) == 'CREATE AND EDIT..' and \
    #         #         data.get('vessel_name_cache', False) == data.get('create_vessel_name', False) and \
    #         #         data.get('vessel_imo_number_cache', False) == data.get('create_imo_number', False) and \
    #         #         data.get('vessel_nrt_cache', False) == data.get('create_vessel_nrt', False) and \
    #         #         data.get('vessel_flag_cache', False) == data.get('create_vessel_flag', False) and \
    #         #         data.get('vessel_crew_num_cache', False) == data.get('create_vessel_crew', False) and \
    #         #         data.get('vessel_name_type_cache', False) == data.get('create_vessel_id', False):
    #         #         skip_create_vessel = True
    #
    #         #store vessel name created from checkout page (request form)
    #         # if data.get('vessel_name', False) == 'CREATE AND EDIT..' and skip_create_vessel:
    #         #     # create new shipping agent
    #         #     vessel_name = data.get('create_vessel_name', False)
    #         #     imo_number = data.get('create_imo_number', False)
    #         #     vessel_id = data.get('create_vessel_id', False)
    #         #     vessel_nrt = data.get('create_vessel_nrt', False)
    #         #     vessel_flag = data.get('create_vessel_flag', False)
    #         #     vessel_crew = data.get('create_vessel_crew', False)
    #         #     # shipping_agent_id = data.get('create_shipping_agent_id', False)
    #         #
    #         #     if not (vessel_name and imo_number and vessel_id and vessel_nrt and vessel_flag and vessel_crew):
    #         #         return res
    #         #
    #         #     try:
    #         #         if vessel_name and imo_number and vessel_id and vessel_nrt and vessel_flag and vessel_crew:
    #         #             vessel_name_env = request.env['vessel.name']
    #         #
    #         #             existing = vessel_name_env.search(
    #         #                 [('name', '=', vessel_name), ('imo_number', '=', imo_number), ('type', '=', vessel_id),
    #         #                  ('nrt','=',vessel_nrt),('flag','=',vessel_flag),('crew','=',vessel_crew),
    #         #                  # ('shipping_agent','=',shipping_agent_id)
    #         #                  ])
    #         #             if not existing.exists():
    #         #                 new_vessel_name = vessel_name_env.sudo().create({'name': vessel_name, 'imo_number': imo_number,
    #         #                                                                'type': vessel_id, 'nrt': vessel_nrt, 'flag': vessel_flag,
    #         #                                                                 'crew': vessel_crew,
    #         #                                                                  # 'shipping_agent': shipping_agent_id
    #         #                 })
    #         #             else:
    #         #                 new_vessel_name = existing
    #         #         else:
    #         #             _logger.error('unable to create vessel name!')
    #         #             raise Exception
    #         #
    #         #         if new_vessel_name.exists():
    #         #             order_data.update({'vessel_name': new_vessel_name.id})
    #         #         else:
    #         #             _logger.error('new_vessel_name does not exist!!')
    #         #             raise Exception
    #         #
    #         #     except Exception as e:
    #         #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         #         _logger.error('Exception Type: ' + str(exc_type))
    #         #         _logger.error('Exception Error Description: ' + str(exc_obj))
    #         #         _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(
    #         #             exc_tb.tb_frame.f_code.co_filename))
    #         #         _logger.error('unable to create new vessel name!')
    #
    #         # else:
    #         #     order_data.update({'vessel_name': data.get('vessel_name', False)})
    #
    #         if order_data['estimated_arrival'] == '':
    #             order_data['estimated_arrival'] = None
    #
    #         sale_order.sudo().write(order_data)
    #
    #
    #         #  _____      _     _   _
    #         # | ____|_  _(_)___| |_(_)_ __   __ _
    #         # |  _| \ \/ / / __| __| | '_ \ / _` |
    #         # | |___ >  <| \__ \ |_| | | | | (_| |
    #         # |_____/_/\_\_|___/\__|_|_| |_|\__, |
    #         #                               |___/
    #         #   ____ _                     _ _
    #         #  / ___| |__   __ _ _ __   __| | | ___ _ __ ___
    #         # | |   | '_ \ / _` | '_ \ / _` | |/ _ \ '__/ __|
    #         # | |___| | | | (_| | | | | (_| | |  __/ |  \__ \
    #         #  \____|_| |_|\__,_|_| |_|\__,_|_|\___|_|  |___/
    #         chan_env = request.env['dp.chandler.temp']
    #         soc_env = request.env['sale.order.chandler']
    #         if sale_order.sudo().many_chandler.exists():
    #             sale_order.sudo().many_chandler.unlink()
    #         chan_on = [data.get('chandler_checkbox1_name', False), data.get('chandler_checkbox2_name', False), data.get('chandler_checkbox3_name', False)]
    #         chan_list = [data.get('chandler_autocomplete_input%s'%str(i+1)) for i in range(len(chan_on)) if chan_on[i]]
    #         chandlers = chan_env.search([('name', 'in', chan_list), ('state', '=', 'approved')])
    #         res['checkout']['chandlers'] = chandlers
    #         try:
    #             assert len(chan_list) == len(chandlers)
    #         except AssertionError as ae:
    #             exc_type, exc_obj, exc_tb = sys.exc_info()
    #             _logger.error('Exception Type: ' + str(exc_type))
    #             _logger.error('Exception Error Description: ' + str(exc_obj))
    #             _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
    #             _logger.error('Possible of duplicate chandlers found')
    #
    #         chan_admin = chan_env.get_one_chandler_admin()
    #         seq = 0
    #         for chan in chandlers:
    #             seq = chan_list.index(chandlers[0].name) + 1
    #             soc_env.sudo().create({
    #                             'chandler': chan.id,
    #                             'seq': seq,
    #                             'active': True,
    #                             'order_id': sale_order.id
    #             })
    #
    #         #  ____                                                   _
    #         # |  _ \ ___  ___ ___  _ __ ___  _ __ ___   ___ _ __   __| |
    #         # | |_) / _ \/ __/ _ \| '_ ` _ \| '_ ` _ \ / _ \ '_ \ / _` |
    #         # |  _ <  __/ (_| (_) | | | | | | | | | | |  __/ | | | (_| |
    #         # |_| \_\___|\___\___/|_| |_| |_|_| |_| |_|\___|_| |_|\__,_|
    #         #
    #         #   ____ _                     _ _
    #         #  / ___| |__   __ _ _ __   __| | | ___ _ __ ___
    #         # | |   | '_ \ / _` | '_ \ / _` | |/ _ \ '__/ __|
    #         # | |___| | | | (_| | | | | (_| | |  __/ |  \__ \
    #         #  \____|_| |_|\__,_|_| |_|\__,_|_|\___|_|  |___/
    #         skipper = {1: False, 2: False, 3: False}
    #         if data:
    #             if data.get('recommend_chandler_name1_cache', False) == data.get('recommend_chandler_name1', False) and \
    #                 data.get('recommend_chandler_email1_cache', False) == data.get('recommend_chandler_email1', False):
    #                 skipper[1] = True
    #             if data.get('recommend_chandler_name2_cache', False) == data.get('recommend_chandler_name2', False) and \
    #                 data.get('recommend_chandler_email2_cache', False) == data.get('recommend_chandler_email2', False):
    #                 skipper[2] = True
    #             if data.get('recommend_chandler_name3_cache', False) == data.get('recommend_chandler_name3', False) and \
    #                 data.get('recommend_chandler_email3_cache', False) == data.get('recommend_chandler_email3', False):
    #                 skipper[3] = True
    #         num_of_loop = [data.get('recommend_chandler_name{}'.format(i), False) for i in range(0,len(data)) if data.get('recommend_chandler_name{}'.format(i), False) is not False]
    #
    #         def chandler_exist(name):
    #             dct = request.env['dp.chandler.temp'].sudo().search([('name', '=', name)])
    #             return dct
    #
    #         for i in range(len(num_of_loop)):
    #             name = data.get('recommend_chandler_name{}'.format(i+1), False)
    #             if name not in ("", False):
    #                 if not confirm and not skipper[i+1]:
    #                     email =  data.get('recommend_chandler_email{}'.format(i+1), False)
    #                     existing_chan = chandler_exist(name.strip())
    #                     if existing_chan.exists():
    #                         new_chan = existing_chan
    #                     else:
    #                         new_chan = chan_env.create({'name': name.strip(), 'email': email.strip(), 'chandler_priority': i+1,
    #                                                     'state': 'draft',
    #                                                     'approver_id': chan_admin.partner_id.id})
    #
    #                     seq += 1
    #                     soc_env.sudo().create({
    #                         'chandler': new_chan.id,
    #                         'seq': seq,
    #                         'active': True,
    #                         'order_id': sale_order.id
    #                     })
    #
    #     res['cache'] = self.get_empty_cache()
    #     return res

    @http.route('/_website_sale/_update_chanler_list', type="json", auth="user")
    def update_chandler_list(self, **kwargs):
        uid = request.session.get('uid', False)
        user_id = request.env['res.users'].browse(uid)
        if user_id:
            chandler_env = request.env['dp.chandler.partner']
            current_chandler = user_id.chandler_list_for_shipmaster
            chan_id = False

            if kwargs.has_key('chandler1_id'):
                chan_id = kwargs.get('chandler1_id')
            # elif kwargs.has_key('chandler1_prefer_id'):
            #     chan_id = kwargs.get('chandler1_prefer_id')

            if kwargs.has_key('chandler2_id'):
                chan_id = kwargs['chandler2_id']
            # elif kwargs.has_key('chandler2_prefer_id'):
            #     chan_id = kwargs.get('chandler2_prefer_id')

            if kwargs.has_key('chandler3_id'):
                chan_id = kwargs['chandler3_id']
            # elif kwargs.has_key('chandler3_prefer_id'):
            #     chan_id = kwargs.get('chandler3_prefer_id')

            # chan_id is dp_chandler_temp fkey
            # need to convert to dp_chandler_partner fkey
            # using partner_id or user_id

            dct = request.env['dp.chandler.temp']
            if chan_id:
                dct = dct.sudo().browse(int(chan_id))
                if dct.exists():
                    dct.ensure_one()
                chan_id = dct.partner_id.id or None

            previous_chan = int(kwargs.get('previous_chandler', False))
            priority = int(kwargs.get('priority', False))
            try:
                chan_id = int(chan_id)
                if len(current_chandler) >= int(kwargs.get('priority', 0)):
                    for chan in current_chandler:
                        if chan.priority == priority:
                            chan.write({'chandler_id': chan_id})
                else:
                    dcp = request.env['dp.chandler.partner']
                    user_id = request.session.get('uid', False)
                    user_obj = request.env['res.users'].browse(user_id)
                    partner_id = user_obj.partner_id.id
                    chandler_temp_id =  dct.id
                    dcp.sudo().create({
                        'priority': priority,
                        'shipmaster_id': partner_id,
                        'chandler_id': chan_id,
                        'chandler_temp_id': chandler_temp_id,
                    })

            except:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                _logger.error('update_chandler_list, unable to convert chandler id into integer and update chandler_list!')


    @http.route('/website_sale/get_chandler_list', type="json", auth="public")
    def get_chandler_list(self, **kwargs):
        chan_obj = request.env['dp.chandler.temp'].sudo().search([('state','=','approved')])
        rtn_dict = {"chandlers": [chan.name for chan in chan_obj],
                    "chandlers_email": [chan.email for chan in chan_obj],}
        return json.dumps(rtn_dict)

    @http.route('/website_sale/get_port_list', type="json", auth="public")
    def get_port_list(self, **kwargs):
        request.env.cr.execute("""select concat(code,': ' ,name) from custom_port""")
        rtn_dict = {"port": [tup[0] for tup in request.env.cr.fetchall()]}
        return json.dumps(rtn_dict)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}
        product_virtual_available = request.env['product.product'].browse(product_id).product_tmpl_id.virtual_available
        if set_qty > product_virtual_available:
            value = {'line_id': line_id, 'quantity':set_qty}
            value['cart_quantity'] = order.cart_quantity
            value['website_sale.total'] = request.website._render("website_sale.total", {
                'website_sale_order': request.website.sale_get_order()
            })
            return value

        value = order.with_context(skip_check_qty=True)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        if not order.cart_quantity:
            request.website.sale_reset()
            return {}

        if not display:
            return None
        value['cart_quantity'] = order.cart_quantity
        value['website_sale.total'] = request.website._render("website_sale.total", {
            'website_sale_order': request.website.sale_get_order()
        })
        return value

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        cr, uid, context = request.cr, request.uid, request.context

        # order = request.website.sale_get_order(force_create=1, context=context)
        #
        # order_line_num = len(order.order_line)
        # counter = 0
        # insufficient_product = ""
        # for order_line in order.order_line:
        #     if order_line.product_uom_qty <= order_line.product_tmpl_id.virtual_available:
        #         counter += 1
        #     else:
        #         insufficient_product += '<li>' + order_line.product_tmpl_id.name + '</li>'
        #
        # if counter == order_line_num:
        #     redirection = self.checkout_redirection(order)
        #     if redirection:
        #         return redirection

        values = self.checkout_values()
        return request.website.render("website_sale.checkout", values)

        # else:
        #     insufficient_values = {'insufficient_product': insufficient_product, 'insufficient': 1}
        #     return request.website.render("website_sale.cart", insufficient_values)

    #TODO: BinhTT override this function to pending error,
    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(context=context)
        if not order:
            return request.redirect("/shop")

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values(post)

        values["error"] = self.checkout_form_validate(values["checkout"])
        if values.has_key('checkout'):
            if values['checkout'].get('date_order', False) not in ('', False) and values['checkout'].get('estimated_arrival', False) not in ('', False):
                do = dt.strptime(values['checkout']['date_order'], '%d/%m/%Y')
                try:
                    ea = dt.strptime(values['checkout']['estimated_arrival'], '%d/%m/%Y')
                except:
                    ea = dt.strptime('01/01/1001', '%d/%m/%Y')
                if ea < do:
                    values["error"].update({'estimated_arrival': 'missing'})
        if values["error"]:
            values['cache'] = self.get_sale_order_information(post)
            return request.website.render("website_sale.checkout", values)

        self.checkout_form_save(values["checkout"])

        request.session['sale_last_order_id'] = order.id

        request.website.sale_get_order(update_pricelist=True, context=context)

        return request.redirect("/shop/payment")

    def get_empty_cache(self):
        return {
            'contact_person': '', 'contact_number': '', 'contact_email': '',
            'vessel_name_dropdown': '',
            'vessel_name': '', 'vessel_imo': '', 'vessel_name_type': '', 'vessel_nrt': '', 'vessel_flag': '',
            'vessel_crew_num': '', 'vessel_type': '',
            'imo_number': '',
            'shipping_agent_dropdown': '',
            'shipping_agent_name': '', 'shipping_agent_contact': '', 'shipping_agent_cr_num': '',
            'call_sign': '', 'next_port': '', 'last_port': '',
            'stay_duration': '', 'estimated_arrival': '',
            'chandler_checkbox1': '', 'chandler_checkbox2': '', 'chandler_checkbox3': '',
            'chandler_autocomplete_id1': '', 'chandler_autocomplete_id2': '', 'chandler_autocomplete_id3': '',
            'recommend_chandler_name1': '', 'recommend_chandler_email1': '',
            'recommend_chandler_name2': '', 'recommend_chandler_email2': '',
            'recommend_chandler_name3': '', 'recommend_chandler_email3': '',
            'check_confirm_before': False,
        }

    def get_testing_cache(self):
        """
        ONLY USED FOR TESTING CACHE INPUT FIELDS
        :return:
        """
        vessel_obj = request.env['vessel.name'].browse(41893)
        shipping_agent_obj = request.env['shipping.agent'].browse(2218)
        vessel_type_obj = request.env['vessel.type'].browse(99)
        last_port_obj = request.env['custom.port'].browse(21138)
        next_port_obj = request.env['custom.port'].browse(15098)
        return {
            'contact_person': 'hahaha', 'contact_number': '9999999', 'contact_email': 'hahaha',
            'vessel_name_dropdown': vessel_obj.id,
            'vessel_name': 'hahaha', 'vessel_imo': '9999999', 'vessel_name_type': vessel_type_obj.id,
            'vessel_nrt': 'hahaha', 'vessel_flag': 'hahaha',
            'vessel_crew_num': 'hahaha', 'vessel_type': vessel_type_obj.id,
            'imo_number': '9999999',
            'shipping_agent_dropdown': shipping_agent_obj.id,
            'shipping_agent_name': 'hahaha', 'shipping_agent_contact': 'hahaha', 'shipping_agent_cr_num': 'hahaha',
            'call_sign': 'hahaha',
            'next_port': next_port_obj.code+': '+next_port_obj.name,
            'last_port': last_port_obj.code+': '+next_port_obj.name,
            'stay_duration': '999', 'estimated_arrival': '31/08/9999',
            'chandler_checkbox1': 'chandler2', 'chandler_checkbox2': 'chandler2', 'chandler_checkbox3': 'chandler2',
            'chandler_autocomplete_id1': 'hahaha', 'chandler_autocomplete_id2': 'hahaha', 'chandler_autocomplete_id3': 'hahaha',
            'recommend_chandler_name1': 'hahaha', 'recommend_chandler_email1': 'hahaha',
            'recommend_chandler_name2': 'hahaha', 'recommend_chandler_email2': 'hahaha',
            'recommend_chandler_name3': 'hahaha', 'recommend_chandler_email3': 'hahaha',
            'check_confirm_before': True,
        }


    def get_sale_order_information(self, post):
        try:
            lp = post.get('last_port_id', '').split(': ')
            assert len(lp) == 2
            last_port_obj = request.env['custom.port'].search([('code', '=', lp[0]), ('name', '=', lp[1])])
            last_port = last_port_obj.code+': '+last_port_obj.name
        except:
            last_port = ''
            _logger.error('last port: {}'.format(last_port))
        try:
            np = post.get('next_port_id', '').split(': ')
            assert len(np) == 2
            next_port_obj = request.env['custom.port'].search([('code', '=', np[0]), ('name', '=', np[1])])
            next_port = next_port_obj.code+': '+next_port_obj.name
        except:
            next_port = ''
            _logger.error('last port: {}'.format(next_port))
        try:
            if post.get('shipping_agent_id', ''):
                shipping_agent_id = post.get('shipping_agent_id', '')
                shipping_agent_name = request.env['shipping.agent'].search([('id', '=', shipping_agent_id)]).name
            else:
                shipping_agent_name = ''
        except:
            shipping_agent_name = ''
            _logger.error('shipping agent: {}'.format(shipping_agent_name))
        return {
            'contact_person': post.get('name', ''),
            'contact_number': post.get('phone', ''),
            'contact_email': post.get('email', ''),
            'vessel_name_dropdown': post.get('vessel_name', ''),
            'vessel_name': post.get('create_vessel_name', ''),
            'vessel_imo': post.get('create_imo_number', ''),
            'vessel_name_type': post.get('create_vessel_id', ''),
            'vessel_nrt': post.get('create_vessel_nrt', ''),
            'vessel_flag': post.get('create_vessel_flag', ''),
            'vessel_crew_num': post.get('create_vessel_crew', ''),
            'vessel_type': post.get('vessel_type', ''),
            'imo_number': post.get('imo_number', ''),
            'shipping_agent_dropdown': shipping_agent_name or '',
            'shipping_agent_name': post.get('shipping_agent_name', ''),
            'shipping_agent_contact': post.get('shipping_agent_contact', ''),
            'shipping_agent_cr_num': post.get('shipping_agent_cr_number', ''),
            'call_sign': post.get('call_sign', ''),
            'next_port': next_port,
            'last_port': last_port,
            'stay_duration': post.get('stay_duration', ''),
            'estimated_arrival': post.get('estimated_arrival', ''),
            'chandler_checkbox1': post.get('chandler_checkbox1_name', ''),
            'chandler_checkbox2': post.get('chandler_checkbox2_name', ''),
            'chandler_checkbox3': post.get('chandler_checkbox3_name', ''),
            'chandler_autocomplete_id1': post.get('chandler_autocomplete_input1', ''),
            'chandler_autocomplete_id2': post.get('chandler_autocomplete_input2', ''),
            'chandler_autocomplete_id3': post.get('chandler_autocomplete_input1', ''),
            'recommend_chandler_name1': post.get('recommend_chandler_name1', ''),
            'recommend_chandler_email1': post.get('recommend_chandler_email1', ''),
            'recommend_chandler_name2': post.get('recommend_chandler_name2', ''),
            'recommend_chandler_email2': post.get('recommend_chandler_email2', ''),
            'recommend_chandler_name3': post.get('recommend_chandler_name3', ''),
            'recommend_chandler_email3': post.get('recommend_chandler_email3', ''),
            'check_confirm_before': True,
        }

    def checkout_form_validate(self, data):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        # Validation
        error = dict()
        # for field_name in self._get_mandatory_billing_fields():
        #     if not data.get(field_name):
        #         error[field_name] = 'missing'

        if not data.get('name', False):
            error["name"] = 'missing'

        # if not data.get('phone', False):
        #     error["phone"] = 'missing'

        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'missing'

        if not data.get('vessel_name', False):
            error["vessel_name"] = 'missing'

        if data.get('vessel_name') == 'CREATE AND EDIT..':
            if not data.get('create_vessel_name', False):
                error["vessel_name"] = 'missing'
            if not data.get('create_imo_number', False):
                error["vessel_name"] = 'missing'
            if (not data.get('create_vessel_id', False)) or data.get('create_vessel_id') == 'Vessel Type..':
                error["vessel_name"] = 'missing'
            if not data.get('create_vessel_nrt', False):
                error["vessel_name"] = 'missing'
            if not data.get('create_vessel_flag', False):
                error["vessel_name"] = 'missing'
            if not data.get('create_vessel_crew', False):
                error["vessel_name"] = 'missing'
            # if (not data.get('create_shipping_agent_id', False)) or data.get('create_shipping_agent_id') == 'Shipping Agent..':
            #     error["vessel_name"] = 'missing'

        if not data.get('vessel_type', False):
            error["vessel_type"] = 'missing'

        # if not data.get('imo_number', False ) and not data.get('call_sign', False):
        #     error["imo_number"] = 'missing'
        #     error["call_sign"] = 'missing'

        if not data.get('shipping_agent_id', False):
            error["shipping_agent_id"] = 'missing'

        # if not data.get('next_port_id', False):
        #     error["next_port_id"] = 'missing'

        # if not data.get('stay_duration', False):
        #     error["stay_duration"] = 'missing'

        # if not data.get('last_port_id', False):
        #     error["last_port_id"] = 'missing'

        if not data.get('chandlers', False):
            error["select_chandlers"] = 'missing'

        if not data.get('estimated_arrival', False):
            error["estimated_arrival"] = 'missing'
        return error

    # TODO: BinhTT override this function to pass check order.amount_total,
    @http.route('/shop/payment/validate', type='http', auth="public", website=True)
    def payment_validate(self, transaction_id=None, sale_order_id=None, **post):
        """ Method that should be called by the server when receiving an update
        for a transaction. State at this point :

         - UDPATE ME
        """
        cr, uid, context = request.cr, request.uid, request.context
        email_act = None
        sale_order_obj = request.env['sale.order']

        if transaction_id is None:
            tx = request.website.sale_get_transaction()
        else:
            tx = request.env['payment.transaction'].browse(transaction_id)

        if sale_order_id is None:
            order = request.website.sale_get_order(context=context)
        else:
            order = request.env['sale.order'].browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        sale_ids = []
        # TODO: Trigger email here
        if order.exists():
            sale_obj = order
            pending_chandler = request.env['dp.chandler.temp']
            admin_obj = request.env['res.users'].sudo().search([('name', '=', 'Administrator')])
            if not admin_obj.exists():
                admin_obj = request.env['res.users'].sudo().search([('name', '=', 'admin')])

            if sale_obj.exists():
                i = 1
                for chan in sale_obj.many_chandler:
                    context_dict = {}
                    if not isinstance(chan.chandler.state, bool):
                        if chan.chandler.state in ('approved'):
                            context_dict['existing_chandler'] = True

                        if chan.chandler.state in ('draft'):
                            context_dict['other_chandler'] = True

                        sale_id = None
                        if chan.active:
                            new_sale_obj = request.env['sale.order']
                            # if i == 1:
                            sale_dict = {}
                            if chan.chandler.state in ('approved'):
                                sale_dict = {'state': 'chandler_draft',
                                             'user_id': chan.chandler.user_id.id,
                                }
                            elif chan.chandler.state in ('draft', 'pending'):
                                sale_dict = {'state': 'chandler_draft',
                                             'user_id': admin_obj.id,
                                             'pending_user_id': chan.chandler.id,
                                }
                                chan.chandler.state = 'pending'
                                chan.chandler.with_context({'sale_obj': sale_obj}).send_email_to_admin_to_accept_preferred_chandler()
                            else:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                _logger.error('Exception Type: ' + str(exc_type))
                                _logger.error('Exception Error Description: ' + str(exc_obj))
                                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                                _logger.error('dp_website_sale.payment_validate: sale_obj {sale_obj} chandler state error {chandler}, {chanchandler}'.format(sale_obj=str(sale_obj), chandler=str(chan), chanchandler=str(chan.chandler)))

                            try:
                                pricelist_id = chan.chandler.user_id.partner_id.property_product_pricelist_purchase.id
                            except:
                                pricelist_id = None
                            if pricelist_id is not None:
                                sale_dict.update({'pricelist_id': pricelist_id})

                            if sale_dict['pricelist_id'] is False:
                                del sale_dict['pricelist_id']
                            if i != 1:
                                sale_dict.update({'write_id': chan.chandler.user_id.id,
                                                  'user_id': chan.chandler.user_id.id,
                                                  'sale_duplicate_id': sale_obj.id})
                                new_sale_obj = sale_obj.with_context({'shop_payment_validate': True}).sudo().copy(default=sale_dict)
                                sale_id = new_sale_obj.id
                                sale_ids.append(sale_id)
                                for create_chan in sale_obj.many_chandler:
                                    request.env['sale.order.chandler'].sudo().create(
                                        {'chandler': create_chan.chandler.id,
                                         'seq': create_chan.seq,
                                         'active': create_chan.active,
                                         'order_id': sale_id
                                         })
                            else:
                                sale_obj.with_context({'shop_payment_validate': True}).sudo().write(sale_dict)

                                sale_id = sale_obj.id
                                sale_ids.append(sale_id)
                            request.cr.commit()
                            # else:
                            #     sale_dict = {}
                            #     if chan.chandler.state in ('approved'):
                            #         sale_dict = {'create_id': chan.chandler.user_id.id,
                            #
                            #                     'state': 'chandler_draft',
                            #                     }
                            #     elif chan.chandler.state in ('pending'):
                            #         sale_dict = {'create_id': chan.chandler.user_id.id,
                            #                      'write_id': chan.chandler.user_id.id,
                            #                      'user_id': admin_obj.id,
                            #                      'pending_user_id': chan.chandler.id,
                            #                      'state': 'chandler_draft',
                            #                      'sale_duplicate_id': sale_obj.id}
                            #     else:
                            #         exc_type, exc_obj, exc_tb = sys.exc_info()
                            #         _logger.error('Exception Type: ' + str(exc_type))
                            #         _logger.error('Exception Error Description: ' + str(exc_obj))
                            #         _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                            #         _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                            #         _logger.error('dp_website_sale.payment_validate: new_sale_obj chandler state error {chandler}, {chanchandler}'.format(sale_obj=str(sale_obj),
                            #             chandler=str(chan), chanchandler=str(chan.chandler)))
                            #
                            #     try:
                            #         pricelist_id = chan.chandler.user_id.partner_id.property_product_pricelist.id
                            #     except:
                            #         pricelist_id = None
                            #     if pricelist_id is not None:
                            #         sale_dict.update({'pricelist_id': pricelist_id})
                            #
                            #     if sale_dict['pricelist_id'] is False:
                            #         del sale_dict['pricelist_id']
                            #
                            #     new_sale_obj = sale_obj.sudo().copy(default=sale_dict)
                            #     sale_id = new_sale_obj.id
                            #     sale_ids.append(sale_id)
                            i += 1
                            try:
                                proxy = request.env['dp.chandler.temp']
                                len_sale_ids = len(sale_ids)
                                # i = 0
                                threads = []
                                # total_sale_ids_thread = len_sale_ids / CPU
                                # for i in range(0, CPU - 1):
                                t = threading.Thread(target=proxy.send_email_multithreading,
                                                     args=(sale_id, chan.chandler.partner_id.email))
                                # threads.append(t)
                                t.start()
                                # t = threading.Thread(target=proxy.send_email_multithreading,
                                #                      args=(sale_ids[(i + 1) * total_sale_ids_thread:],))
                                # t.start()
                                # threads.append(t)
                                # chan.chandler.send_email_multithreading(request.session, sale_id, context_dict)
                            except Exception:
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                _logger.error('Exception Type: ' + str(exc_type))
                                _logger.error('Exception Error Description: ' + str(exc_obj))
                                _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                                _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
                                _logger.error('Multithreading Problems')



        # if len(sale_ids) > 0:
        #     # try:
        #     #     proxy = request.env['dp.chandler.temp']
        #     #     len_sale_ids = len(sale_ids)
        #     #     i = 0
        #     #     threads = []
        #     #     total_sale_ids_thread = len_sale_ids / CPU
        #     #     for i in range(0, CPU - 1):
        #     #         t = threading.Thread(target=proxy.send_email_multithreading,
        #     #                              args=(sale_ids[i * total_sale_ids_thread: total_sale_ids_thread * (i + 1)],))
        #     #         threads.append(t)
        #     #         t.start()
        #     #     t = threading.Thread(target=proxy.send_email_multithreading,
        #     #                          args=(sale_ids[(i + 1) * total_sale_ids_thread:],))
        #     #     t.start()
        #     #     threads.append(t)
        #     #     # chan.chandler.send_email_multithreading(request.session, sale_id, context_dict)
        #     # except Exception:
        #     #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     #     _logger.error('Exception Type: ' + str(exc_type))
        #     #     _logger.error('Exception Error Description: ' + str(exc_obj))
        #     #     _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
        #     #     _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
        #     #     _logger.error('Multithreading Problems')
        #
        #     def filter_products(product, sale_order_line):
        #         return filter(lambda d: product.id == d.product_id.id, sale_order_line)
        #     try:
        #         stock_alloc_obj = request.env['sale.line.stock.allocation']
        #         sale_objs = request.env['sale.order'].browse(sale_ids)
        #         mapped_products = sale_objs.mapped(lambda a: a.order_line).mapped(lambda b: b.product_id)
        #         sol = sale_objs.mapped(lambda c: c.order_line)
        #         for product in mapped_products:
        #             sale_order_lines =  filter_products(product, sol)
        #             max_qty = max(map(lambda d: d.product_uom_qty, sale_order_lines))
        #             sao = stock_alloc_obj.create({'state': 'ongoing',
        #                                     'name': product.name_template,
        #                                     'product_id': product.id,
        #                                     'product_qty': max_qty
        #                                     })
        #
        #             # sale_order_lines = [sale.order.line(153,), sale.order.line(155,), sale.order.line(157,)]
        #             for line in sale_order_lines:
        #                 line.write({'stock_allocation_id': sao.id})
        #
        #     except Exception as e:
        #         exc_type, exc_obj, exc_tb = sys.exc_info()
        #         _logger.error('Exception Type: ' + str(exc_type))
        #         _logger.error('Exception Error Description: ' + str(exc_obj))
        #         _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
        #         _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
        #         _logger.info('dp_website_sale.payment_validate exception: {e}'.format(e=e))
        #         try:
        #             _logger.info('dp_website_sale.payment_validate sale_objs = {sale_objs}'.format(sale_objs=str(sale_objs)))
        #         except:
        #             pass
        #         try:
        #             _logger.info('dp_website_sale.payment_validate mapped_products = {mapped_products}'.format(mapped_products=str(mapped_products)))
        #         except:
        #             pass
        #         try:
        #             _logger.info('dp_website_sale.payment_validate sol = {sol}'.format(sol=str(sol)))
        #         except:
        #             pass
        # if not order or (order.amount_total and not tx):
        #     return request.redirect('/shop')

        # if (not order.amount_total and not tx) or tx.state in ['pending', 'done']:
        #     if (not order.amount_total and not tx):
        #         # Orders are confirmed by payment transactions, but there is none for free orders,
        #         # (e.g. free events), so confirm immediately
        #         order.with_context(dict(context, send_email=True)).action_button_confirm()
        # order.write({'state': 'chandler_draft'})
        # elif tx and tx.state == 'cancel':
        #     # cancel the quotation
        #     sale_order_obj.action_cancel(cr, SUPERUSER_ID, [order.id], context=request.context)

        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset(context=context)
        # if tx and tx.state == 'draft':
        #     return request.redirect('/shop')
        sale_obj.date_order = datetime.strptime(datetime.strftime(datetime.now(), '%d-%m-%Y %H:%M:%S'), '%d-%m-%Y %H:%M:%S')
        if sale_obj.partner_id:
            if sale_obj.partner_id.user_id.has_group('dp_common.group_chandler'):
                sale_obj.bid_confirm_order()
                # sale_obj.action_button_confirm()

        return request.redirect('/shop/confirmation')

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        cr, uid, context = request.cr, request.uid, request.context

        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            duplicate = request.env['sale.order'].sudo().search([('sale_duplicate_id', '=', order.id)],  order='id')

        else:
            return request.redirect('/shop')

        return request.website.render("website_sale.confirmation", {'order': order, 'duplicate': duplicate})

    @http.route(['/shop_login'], type='http', auth="public", website=True)
    def shop_check_access(self, page=0, category=None, search='', **post):
        session = request.session
        if session.get('login', None) is None and session.get('password', None) is None:
            return request.website.render("web.login")
        return request.redirect("/shop")

    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()

        if search:
            for srch in search.split(" "):
                domain += [('name', 'ilike', srch)]

        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        if post.get('DropdownCategory', False):
            dropdown = post.get('DropdownCategory')
            category = None
            if dropdown != 'ALL PRODUCTS':
                category = request.env['product.public.category'].sudo().search([('name', '=', dropdown)])
        if post.get('DropdownCategory', False) is False and search != '':
            # reset search as clicking side bar menu will still get search
            search = ''

        # order products by name
        post['order'] = 'name'

        data = super(DPwebsite_sale, self).shop(page, category, search, **post)

        category_obj = request.env['product.public.category']
        product_obj = request.env['product.template']
        #check if user has logged in
        all_product_ids = product_obj.search([('website_published', '=', True)])
        if request.uid == 3:
            category_show = all_product_ids.mapped('public_categ_ids').filtered(lambda x: x.hidden_to_public ==  False)
        else:
            category_show = all_product_ids.mapped('public_categ_ids')
        for cate in category_show:
            parent_id = cate.parent_id
            while parent_id and parent_id not in category_show:
                category_show += parent_id
                parent_id = parent_id.parent_id

            # Filter out empty product category
        products_show = request.env['product.template']
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]

        if data.qcontext.get('products'):
            if request.session.get('login', None):
                # user is logged in will be able to see hidden to public products
                products_show = data.qcontext['products'].filtered(lambda x: x.website_published is True)
                all_country_id = all_product_ids.filtered(lambda x: x.website_published is True).mapped('country_id').sorted(lambda x:x.display_name.upper())
                product_obj = request.registry.get('product.template')
                if category:
                    domain = [('sale_ok', '=', True),('public_categ_ids', 'child_of', int(category)), ('website_published', '=', True)]
                elif search:
                    domain = self._get_search_domain(search, category, attrib_values)
                    domain.extend([('website_published', '=', True)])
                else:
                    domain = [('sale_ok', '=', True), ('website_published', '=', True)]
                product_count = product_obj.search_count(request.cr, request.uid, domain, context=None)


            else:
                # products_show = data.qcontext['products'].filtered(lambda x: x.website_published is True and x.hidden_to_public is False)
                all_country_id = all_product_ids.filtered(lambda x: x.website_published is True and x.hidden_to_public is False).mapped('country_id').sorted(lambda x:x.display_name.upper())
                # products_show = data.qcontext['products'].filtered(lambda x: x.website_published is True)
                product_obj = request.registry.get('product.template')
                if category:
                    domain = [('sale_ok', '=', True), ('public_categ_ids', 'child_of', int(category)), ('website_published', '=', True), ('hidden_to_public', '=', False)]
                elif search:
                    domain = self._get_search_domain(search, category, attrib_values)
                    domain.extend([('website_published', '=', True)])
                else:
                    domain = [('sale_ok', '=', True), ('website_published', '=', True), ('hidden_to_public', '=', False)]
                product_count = product_obj.search_count(request.cr, request.uid, domain, context=None)

                # all products with domain filter
                url = "/shop"
                pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
                product_ids = product_obj.search(request.cr, request.uid, domain, limit=PPG, offset=pager['offset'],
                                                 order=self._get_search_order(post), context=request.context)
                # browse object with filtered ids
                products_show = product_obj.browse(request.cr, request.uid, product_ids, context=request.context)
                data.qcontext.update(bins=table_compute().process(products_show))



            url = "/shop"
            if category:
                url = "/shop/category/%s" % slug(category)
            if search:
                post["search"] = search



            pager_updated = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7,
                                                  url_args=post)
            # sort by function
            if post.get('sort_by') and not post.get('filter_by_country'):
                if str(post['sort_by']) == 'name_a_z':
                    product_ids = product_obj.search(request.cr, request.uid, domain, limit=PPG, offset=pager_updated['offset'],
                                                     order='name',
                                                     context=request.context)
                elif str(post['sort_by']) == 'name_z_a':
                    product_ids = product_obj.search(request.cr, request.uid, domain, limit=PPG, offset=pager_updated['offset'],
                                                     order='name desc',
                                                     context=request.context)
                products = product_obj.browse(request.cr, request.uid, product_ids, context=request.context)
                products_show = products
                if request.session.get('login', None):
                    products_show = products_show.filtered(lambda x: x.website_published is True)
                else:
                    products_show = products_show.filtered(
                        lambda x: x.website_published is True and x.hidden_to_public is False)
                data.qcontext.update(bins = table_compute().process(products), sort_by = str(post['sort_by']))
            if post.get('filter_by_country'):
                country_id = post.get('filter_by_country')
                domain.extend([('country_id', '=', int(country_id))])

                if post.get('sort_by'):
                    if str(post['sort_by']) == 'name_a_z':
                        product_ids = product_obj.search(request.cr, request.uid, domain, limit=PPG,
                                                         offset=pager_updated['offset'],
                                                         order='name',
                                                         context=request.context)
                    elif str(post['sort_by']) == 'name_z_a':
                        product_ids = product_obj.search(request.cr, request.uid, domain, limit=PPG,
                                                         offset=pager_updated['offset'],
                                                         order='name desc',
                                                         context=request.context)
                    products = product_obj.browse(request.cr, request.uid, product_ids, context=request.context)
                    products_show = products
                    if request.session.get('login', None):
                        products_show = products_show.filtered(lambda x: x.website_published is True)
                    else:
                        products_show = products_show.filtered(
                            lambda x: x.website_published is True and x.hidden_to_public is False)
                    data.qcontext.update(bins=table_compute().process(products), sort_by=str(post['sort_by']), filter_by_country = str(post['filter_by_country']))
            if request.session.get('login', None):
                product_count = product_obj.search_count(request.cr, request.uid, domain, context=None)
            else:
                res_product = request.env['product.template'].search(domain)
                product_count = len(res_product.filtered(lambda x: x.hidden_to_public is False))
                products_show = products_show.filtered(lambda x: x.hidden_to_public is False)
            pager_updated = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7,
                                                  url_args=post)
            data.qcontext.update(pager=pager_updated)
            data.qcontext.update(category_show=category_show.ids,
                             categories=category_show.search([('id', 'in', category_show.ids), ('parent_id', '=', False)], order='name'),
                             products=products_show, all_country_id=all_country_id)
        else:
            data.qcontext.update(category_show=category_show.ids,
                                 categories=category_show.search(
                                     [('id', 'in', category_show.ids), ('parent_id', '=', False)], order='name'),
                                 products=products_show)
        return data

    @http.route(['/shop/custom_cart_update_json'], type='json', auth="public", methods=['POST'], website=True)
    def custom_cart_update_json(self, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context
        product_id = kwargs.get('product_id', False)
        add_qty, set_qty = 1, 0
        if product_id is not False:
            request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id), add_qty=float(add_qty), set_qty=float(set_qty))
        try:
            return_sum = sum(request.website.sale_get_order(force_create=1).order_line.mapped(lambda x: x.product_uom_qty))
        except:
            return_sum = 0
        return json.dumps({'return_sum': return_sum})

    def checkout_redirection(self, order):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        public_user = request.env['res.users'].sudo().search([('login', '=', 'public'), ('active', '=', False)])
        public_user.ensure_one()
        if order.partner_id.id == public_user.partner_id.id:
            return request.redirect('/shop_login')

        # must have a draft sale order with lines at this point, otherwise reset
        if not order or order.state != 'draft':
            request.session['sale_order_id'] = None
            request.session['sale_transaction_id'] = None
            return request.redirect('/shop')

        # if transaction pending / done: redirect to confirmation
        tx = context.get('website_sale_transaction')
        if tx and tx.state != 'draft':
            return request.redirect('/shop/payment/confirmation/%s' % order.id)



# Todo: all integration start from here

    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        res = super(DPwebsite_sale, self).cart(**post)
        if post.get('type') == 'popover':
            # two qweb responses will be rendered in this case, the one by
            # super and this one, but there is no way around it if
            # we don't want to break inheritance
            return request.website.render(
                "dp_website_sale.cart_popover", res.qcontext)
        return res

    @http.route(['/shop/empty-cart'], type='json', auth='public', methods=['post'], website=True)
    def empty_cart(self):
        request.website.sale_reset()
        return {}

    @http.route('/checkout/get_shipping_agent_list', type="json", auth="public")
    def get_shipping_agent_list(self, **kwargs):
        request.env.cr.execute("""select distinct name from shipping_agent where name is not null and active=True""")
        rtn_dict = {"shipping_agent": [tup[0] for tup in request.env.cr.fetchall()]}
        return json.dumps(rtn_dict)


class elephase_shop(http.Controller):

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        # cr, uid, context = request.cr, request.uid, request.context
        product_product = request.env['product.product'].sudo().browse(int(product_id))

        if product_product.product_tmpl_id.virtual_available >= int(add_qty):
            result = request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id), add_qty=float(add_qty),
                                                                        set_qty=float(set_qty))
            if result.get('quantity', '')>product_product.product_tmpl_id.virtual_available:
                product_name = slug(product_product.product_tmpl_id) + "#?added=false"
                return request.redirect("/shop/product/" + product_name.lower())

            product_name = slug(product_product.product_tmpl_id) + "#?added=true"
            if kw.get('is_shop', False):
                redirect_url = kw.get('is_shop', False)
                if 'added' in redirect_url:
                    return request.redirect(redirect_url)
                else:
                    return request.redirect("%s#?added=true" % (redirect_url))
            return request.redirect("/shop/product/" + product_name.lower())
        else:
            product_name = slug(product_product.product_tmpl_id) + "#?added=false"
            return request.redirect("/shop/product/" + product_name.lower())



class table_compute(object):
    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        for p in products:
            x = min(max(p.website_size_x, 1), PPR)
            y = min(max(p.website_size_y, 1), PPR)
            if index >= PPG:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % PPR, pos / PPR, x, y):
                pos += 1
            # if 21st products (index 20) and the last line is full (PPR products in it), break
            # (pos + 1.0) / PPR is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= PPG and ((pos + 1.0) / PPR) > maxy:
                break

            if x == 1 and y == 1:  # simple heuristic for CPU optimization
                minpos = pos / PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos / PPR) + y2][(pos % PPR) + x2] = False
            self.table[pos / PPR][pos % PPR] = {
                'product': p, 'x': x, 'y': y,
                'class': " ".join(map(lambda x: x.html_class or '', p.website_style_ids))
            }
            if index <= PPG:
                maxy = max(maxy, y + (pos / PPR))
            index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows
        # TODO keep with input type hidden
website_sale.table_compute = table_compute

class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k, v in self.args.items():
            kw.setdefault(k, v)
        l = []
        for k, v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k, i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k, v)]))
        if l:
            path += '?' + '&'.join(l)
        return path