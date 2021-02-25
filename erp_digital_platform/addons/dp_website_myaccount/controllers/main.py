# -*- coding: utf-8 -*-
import logging, json
import werkzeug

from openerp import SUPERUSER_ID
from openerp import http, sql_db
from openerp import tools
from openerp.http import request
import sys
from openerp.tools.translate import _
# from openerp.addons.website.models.website import slug
# from openerp.addons.web.controllers.main import login_redirect
_logger = logging.getLogger(__name__)

class website_account(http.Controller):

    @http.route('/myaccounts/get_vessel_name', type="json", auth="public")
    def get_port_list(self, **kwargs):
        request.env.cr.execute("""select distinct name from vessel_name""")
        rtn_dict = {"vessel_name": [tup[0] for tup in request.env.cr.fetchall()]}
        return json.dumps(rtn_dict)

    @http.route(['/myaccounts'], type='http', auth='user', website=True)
    def get_myaccount_info(self, **kw):
        # Below code commented as per Bin instruction.

        partner_obj = request.env['res.partner']
        user_obj = request.env['res.users']
        user_id = user_obj.search([('id', '=',request.session.uid )])
        partner_id = user_id.partner_id
        vessel_obj = request.env['vessel.type'].search([], order='name')
        # vessel_name_obj = request.env['vessel.name'].search([])
        shipping_obj = request.env['shipping.agent'].search([])
        # partner_data = partner_obj.search([('id', '=', user_id.partner_id.id)])
        # tmp_dict = {}
        # indx = 1
        # for pc in partner_data.chandler_list_for_shipmaster:
        #     tmp_dict['pc_{}'.format(indx)] = pc.chandler_id.name
        #     indx += 1

        values = {
            'from_enquiry': 'inactive',

            'email': user_id.email or '',
            'vname': partner_id.vessel_name or '',
            'vtype': partner_id.vessel_type or '',
            'vessel_obj': vessel_obj,
            # 'vessel_name_obj': vessel_name_obj,
            'shipping_obj': shipping_obj,
            'name': user_id.name or '',
            'tel': user_id.phone or '',
            'imo': partner_id.imo_number or '',
            'call_sign': partner_id.call_sign or '',
            'pc_1': '',
            'pc_2': '',
            'pc_3': ''
        }

        chandler_ids = partner_id.sudo().chandler_list_for_shipmaster
        for i in range(len(chandler_ids)):
            values.update({'pc_%d'%(i+1): chandler_ids[i].chandler_id.name})

        # if tmp_dict:
        #     values.update(tmp_dict)
        return request.website.render("dp_website_myaccount.myaccount_info", values)

    @http.route(['/myenquiry'], type='http', auth='user', website=True)
    def get_myenquiry_info(self, **kw):
        values = self.get_value_myenquiry()
        return request.website.render("dp_website_myaccount.myaccount_info", values)


    def get_value_myenquiry(self):

        user = request.env['res.users'].browse(request.uid)
        partner_id = user.partner_id
        sale_env = request.env['sale.order'].sudo().search([('partner_id', '=', partner_id.id), ('order_line', '!=', False), ('state', 'not in', ('draft',))], order="date_order desc", limit=10)
        values = {
            'from_enquiry': 'active',
            'orders': sale_env,
            'name': user.name or False
        }
        return values

    @http.route('/_website_myaccount/_get_approved_chandler_list', type="json",  auth="public")
    def _get_approved_chandler_list(self, **kwargs):
        try:
            # _logger.info(json.dumps({'approved_chandlers': [obj.name for obj in \
            #                                   request.env['dp.chandler.temp'].sudo().search([('active', '=', True)])]}))
            return json.dumps({'approved_chandlers': [obj.name for obj in \
                                              request.env['dp.chandler.temp'].sudo().search([('active', '=', True),
                                                                                             ('state', '=', 'approved')])]})
        except:
            _logger.info('NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING NOTHING ')
            return json.dumps({'approved_chandlers': []})

    @http.route('/_website_myaccount/check_vessel_name', type="json", auth="user",  website=True)
    def check_vessel_name_exist(self, **kwargs):
        vessel_name = request.env['vessel.name']
        if vessel_name.search([('name', '=', kwargs.get('value'))]):
            return True

        return False

    @http.route('/_website_myaccount/_update_account_info', type="json", auth="user",  website=True)
    def update_account_info(self, **kwargs):
        # kwargs["error"] = self.checkout_form_validate(kwargs)
        # if kwargs["error"]:
        #     return request.website.render("/myaccounts", kwargs)

        uid = request.session.get('uid', False)
        user_id = request.env['res.users'].browse(uid)
        if user_id:
            """
            kwargs = {
                     'call_sign': u'callsign123',
                     'email': u'itdevpptech@gmail.com',
                     'imo': u'imonumb',
                     'name': u'ShipMaster1',
                     'pc_one': u'Google',
                     'pc_three': u'Guugle',
                     'pc_two': u'Gaagle',
                     'tel': u'98765432',
                     'vname': u'vessname',
                     'vtype': u'vesstype'}
            
            values = {
                'from_enquiry': 'inactive',
                'email': user_id.email or '',
                'vname': partner_id.vessel_name or '',
                'vtype': partner_id.vessel_type or '',
                'name': user_id.name or '',
                'tel': user_id.phone or '',
                'imo': partner_id.imo_number or '',
                'call_sign': partner_id.call_sign or '',
                'pc_1': '',
                'pc_2': '',
                'pc_3': ''
            }
            """
            partner_id = user_id.partner_id
            imo_num = kwargs['value'].get('imo', None)
            call_sign = kwargs['value'].get('call_sign', None)
            vtype = kwargs['value'].get('vtype', None)
            vname = kwargs['value'].get('vname', None)

            partner_data = {}
            if vname == "CREATE AND EDIT..":
                vessel_name = kwargs['value'].get("vessel_name_id", False)
                imo_number = kwargs['value'].get("imo_number_id", False)
                vessel_id = kwargs['value'].get("vessel_type_select_id", False)
                vessel_nrt = kwargs['value'].get("vessel_nrt_id", False)
                vessel_flag = kwargs['value'].get("vessel_flag_id", False)
                vessel_crew = kwargs['value'].get("vessel_crew_id", False)
                # shipping_agent_id = kwargs['value'].get("shipping_agent_select_id", False)

                try:
                    if vessel_name and imo_number and vessel_id and vessel_nrt and vessel_flag and vessel_crew:
                        vessel_name_env = request.env['vessel.name']

                        existing = vessel_name_env.search(
                            [('name', '=', vessel_name), ('imo_number', '=', imo_number), ('type', '=', vessel_id),
                             ('nrt', '=', vessel_nrt), ('flag', '=', vessel_flag), ('crew', '=', vessel_crew),
                             ])
                        if not existing.exists():
                            new_vessel_name = vessel_name_env.sudo().create(
                                {'name': vessel_name, 'imo_number': imo_number,
                                 'type': vessel_id, 'nrt': vessel_nrt,
                                 'flag': vessel_flag,
                                 'crew': vessel_crew,
                                 })
                        else:
                            new_vessel_name = existing
                    else:
                        _logger.error('unable to create vessel name!')
                        raise Exception

                    if new_vessel_name.exists():
                        partner_data = {
                            'imo_number': imo_num,
                            'call_sign': call_sign,
                            'vessel_name': new_vessel_name.name,
                            'vessel_type': vtype
                        }
                    else:
                        _logger.error('new_vessel_name does not exist!!')
                        raise Exception

                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    _logger.error('Exception Type: ' + str(exc_type))
                    _logger.error('Exception Error Description: ' + str(exc_obj))
                    _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(
                        exc_tb.tb_frame.f_code.co_filename))
                    _logger.error('unable to create new vessel name!')

            else:
                partner_data = {
                    'imo_number': imo_num,
                    'call_sign': call_sign,
                    'vessel_name': vname,
                    'vessel_type': vtype
            }
            email = kwargs['value'].get('email', None)
            name = kwargs['value'].get('name', None)
            tel = kwargs['value'].get('tel', None)
            user_data = {
                            'email': email,
                            'name': name,
                            'phone': tel,
            }

            name_list = [kwargs['value'].get('pc_one', False), kwargs['value'].get('pc_two', False), kwargs['value'].get('pc_three', False)]
            name_list = [i for i in name_list if i is not False]
            blank_pref_chan_priority = [i+1 for i, x in enumerate(name_list) if not x]
            if blank_pref_chan_priority:
                for index in blank_pref_chan_priority:
                    if index in partner_id.chandler_list_for_shipmaster.mapped(lambda x: x.priority):
                        partner_id.chandler_list_for_shipmaster[blank_pref_chan_priority[0]-1].sudo().unlink()
            chandlers = request.env['dp.chandler.temp'].sudo().search([('name', 'in', name_list)])
            try:
                for chan in chandlers:
                    if kwargs['value'].get('pc_one', False) == chan.name:
                        priority = 1
                    elif kwargs['value'].get('pc_two', False) == chan.name:
                        priority = 2
                    elif kwargs['value'].get('pc_three', False) == chan.name:
                        priority = 3
                    else:
                        priority = None
                    chandler_partner_dict = {
                        'shipmaster_id': partner_id.id,
                        'chandler_id': chan.partner_id.id,
                    }

                    if priority in partner_id.chandler_list_for_shipmaster.mapped(lambda x: x.priority):
                        # write existing
                        for exist_chan in partner_id.chandler_list_for_shipmaster:
                            if exist_chan.priority == priority:
                                exist_chan.write(chandler_partner_dict)
                    else:
                        # create new
                        if priority is not None:
                            chandler_partner_dict['priority'] = priority
                            self._create_chandler_for_shipmaster(chandler_partner_dict)
                        else:
                            raise Exception
            except Exception as e:
                _logger.error(e)
                _logger.error('Error in create_chandler_partner_info name_list: {}'.format(name_list))
                _logger.error('Error in create_chandler_partner_info chandlers: {}'.format(chandlers))

            partner_written = False
            try:
                partner_id.write(partner_data)
                partner_written = True
            except Exception as e:
                _logger.error(e)
                _logger.error('Error in update_partner_info kwargs: {}'.format(json.dumps(kwargs, separators=(',', ':'))))
                _logger.error('Error in update_partner_info partner_data: {}'.format(json.dumps(partner_data, separators=(',', ':'))))

            user_written = False
            try:
                user_id.write(user_data)
                user_written = True
            except Exception as e:
                _logger.error(e)
                _logger.error('Error in update_account_info kwargs: {}'.format(json.dumps(kwargs, separators=(',', ':'))))
                _logger.error('Error in update_account_info user_data: {}'.format(json.dumps(user_data, separators=(',', ':'))))

            if partner_written and user_written:
                # url = http.request.env['ir.config_parameter'].get_param('web.base.url')
                # return http.request.redirect("/myaccounts", kwargs)
                # return request.website._render("myaccounts", {'success': False})
                val = True
                return val
    # def checkout_form_validate(self, data):
    #     cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
    #
    #     # Validation
    #     error = dict()
    #
    #     if not bool(data.get('name')):
    #         error["name"] = 'missing'
    #
    #     if not bool(data.get('tel')):
    #         error["tel"] = 'missing'
    #
    #     if data.get('email') and not tools.single_email_re.match(data.get('email')):
    #         error["email"] = 'missing'
    #
    #     if data.get('vname') == 'CREATE AND EDIT..':
    #         if not bool(data.get('vessel_name_id')):
    #             error["vessel_name_select_name"] = 'missing'
    #         if not bool(data.get('imo_number_id')):
    #             error["vessel_name_select_name"] = 'missing'
    #         if not bool(data.get('vessel_name_id')):
    #             error["vessel_name_select_name"] = 'missing'
    #         if not bool(data.get('vessel_nrt_id')):
    #             error["vessel_name_select_name"] = 'missing'
    #         if not bool(data.get('vessel_nrt_id')):
    #             error["vessel_name_select_name"] = 'missing'
    #         if not bool(data.get('vessel_crew_id')):
    #             error["vessel_name_select_name"] = 'missing'
    #         if (not bool(data.get('shipping_agent_select_id'))) or data.get('shipping_agent_select_id') == 'Shipping Agent..':
    #             error["vessel_name_select_name"] = 'missing'
    #
    #     if not bool(data.get('vtype')):
    #         error["vessel_type_select_name"] = 'missing'
    #
    #     if not bool(data.get('call_sign')):
    #         error["call_sign"] = 'missing'
    #
    #     return error

    def _create_chandler_for_shipmaster(self, param):
        request.env['dp.chandler.partner'].create(param)

    @http.route(['/changepassword'],  type='json',  methods=['POST'], auth="user", website=True)
    def change_password(self, old_password=None, new_password=None, **kw):
        if request.context.get('open_form', False):
            return request.website._render("dp_website_myaccount.modal", {})
        new_password = new_password.strip()
        if old_password != None and new_password != None:
            user_obj = request.env['res.users'].browse(request.uid)

            try:
                if user_obj.change_password(
                        old_password, new_password):
                    user_obj.myaccount_reset_password_send_alert_email()
                    return True
            except Exception:
                return request.website._render("dp_website_myaccount.wrong_password", {'success': False})
