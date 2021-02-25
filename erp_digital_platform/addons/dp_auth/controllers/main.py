# -*- coding: utf-8 -*-
import werkzeug
import logging, sys, json
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
import openerp.addons.auth_signup.controllers.main as main
from openerp.addons.auth_signup.res_users import SignupError
from datetime import datetime as dt

_logger = logging.getLogger(__name__)


class SignupExtend(main.AuthSignupHome):

    def signup_form_validate(self, data):
        error = dict()
        # if not data.get('name', False):
        #     error["name"] = 'missing'
        if not data.get('password', False):
            error["password"] = 'missing'
        if not data.get('confirm_password', False):
            error["confirm_password"] = 'missing'
        # if not data.get('vessel_id', False):
        #     error["vessel_id"] = 'missing'
        # if not data.get('vessel_name', False):
        #     error["vessel_name"] = 'missing'
        # if data.get('vessel_name', False):
        #     if not request.env['vessel.name'].search([('name', '=', data.get('vessel_name').upper())]):
        #         error["vessel_name"] = 'missing'
        #         data.update(invalid_vessel_name = data.get('vessel_name'))
        return error

    @http.route('/web/signup', type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        """Override the default method."""
        vessel_obj = request.env['vessel.type'].search([], order='name')
        vessel_name_obj = request.env['vessel.name'].search([])
        shipping_obj = request.env['shipping.agent'].search([])
        try:
            qcontext = self.get_auth_signup_qcontext()
            qcontext.update({'vessel_obj': vessel_obj})
            qcontext.update({'vessel_name_obj': vessel_name_obj})
            qcontext.update({'shipping_obj': shipping_obj})
            if 'error' not in qcontext and request.httprequest.method == 'POST':
                qcontext.update({"error": self.signup_form_validate(qcontext)})
                if qcontext.get('error', False):
                    return request.render('auth_signup.signup', qcontext)
                # if not qcontext.get("imo", False) and not qcontext.get("call_sign", False):
                #     qcontext["error"] = _("Please provide IMO Number or Call Sign information.")
                #     return request.render('auth_signup.signup', qcontext)
                # list_chandlers = []
                # chandler_id = self.check_dp_chandler_user_by_name(qcontext.get('pc_one'))
                # list_chandlers.append(qcontext.get("pc_one"))
                # if not chandler_id['status']:
                #     qcontext["error"] = _("Please provide correct chandler name")
                #     return request.render('auth_signup.signup', qcontext)

                # if qcontext.get("pc_two", False):
                #     list_chandlers.append(qcontext.get("pc_two"))
                #     chandler_id = self.check_dp_chandler_user_by_name(qcontext.get('pc_two'))
                #     if not chandler_id['status']:
                #         qcontext["error"] = _("Please provide correct #2 chandler name")
                #         return request.render('auth_signup.signup', qcontext)
                #
                # if qcontext.get("pc_three", False):
                #     list_chandlers.append(qcontext.get("pc_three"))
                #     chandler_id = self.check_dp_chandler_user_by_name(qcontext.get('pc_three'))
                #     if not chandler_id['status']:
                #         qcontext["error"] = _("Please provide correct #3 chandler name")
                #         return request.render('auth_signup.signup', qcontext)

                # if list_chandlers:
                #     is_dp_found = self.find_duplicate_chandler(list_chandlers)
                #     if is_dp_found:
                #         qcontext["error"] = _("Please provide unique chandler names.")


            else:
                if 'inv_id' in qcontext:
                    user_response = self.check_dp_chandler_limit(qcontext)
                    qcontext.update({"error": {}})
                    if user_response.has_key('tot_chandlers'):
                        if user_response.get('user_found') == "No":
                            qcontext.update(user_response)
                            return request.render('auth_signup.signup', qcontext)
                        else:
                            qcontext.update(user_response)
                            # return http.request.redirect("/page/confirm_chandler?inv_id={}".format(qcontext.get("inv_id")))
                            return http.request.redirect("/web/login")
                    else:
                        qcontext.update(error_account="Looks like you already have an account with us. Would you like to log in or recover your password?")
                        return request.render("auth_signup.signup", qcontext)
                if 'token' in qcontext:
                    qcontext.update({"error": {}, "chandler_signup": True})
                    user_obj = request.env['res.users']
                    user_id = user_obj.sudo().search([('login', '=', qcontext.get('login', ''))])
                    try:
                        assert len(user_id) == 1
                        qcontext.update(pc_one = user_obj.sudo().search([('name', '=', 'BTF Sales')]).name)
                        return request.render('auth_signup.signup', qcontext)
                    except:
                        return request.render('auth_signup.signup', qcontext)

        except Exception as e:
            _logger.error(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('web_auth_signup:  -------------------------------------------------------------------------')

        rtn = super(SignupExtend, self).web_auth_signup(*args, **kw)
        rtn.qcontext.update({'vessel_obj': vessel_obj})
        rtn.qcontext.update({'vessel_name_obj': vessel_name_obj})
        rtn.qcontext.update({'shipping_obj': shipping_obj})
        rtn.qcontext.update({'error': {}})
        # insert chandler joined time
        chand = request.env['dp.chandler.temp'].sudo().search([('email', '=', qcontext.get('login'))])
        if chand:
            chand.joined_date = dt.now()
        # if qcontext.get('login', False):
        #     request.env['dp.shipmaster.invitation'].sudo().search([('shipmaster_email','=', qcontext.get('login'))], limit=1).joined_date = dt.now()
        return rtn
        # return request.render('auth_signup.signup', qcontext)

    @http.route('/web/reset_password', type='http', auth='public', website=True)
    def web_auth_reset_password(self, *args, **kw):
        """Default method override."""
        qcontext = self.get_auth_signup_qcontext()
        qcontext.update({'error': {}})
        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        # if 'error' not in qcontext and request.httprequest.method == 'POST':
        if not qcontext.get('error', False) and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    user_obj = request.env['res.users'].browse(request.session.get('uid', 0))
                    if user_obj.exists():
                        user_obj.sudo().web_reset_password_send_alert_email(qcontext)
                    return super(SignupExtend, self).web_login(*args, **kw)
                else:
                    if qcontext.get("reset_request"):
                        login = qcontext.get('login')
                        assert login, "No login provided."
                        res_users = request.env['res.users']
                        res_users.sudo().reset_password(login)
                        qcontext['message'] = _("An email has been sent to reset your password.")
                    else:
                        login = qcontext.get('login')
                        assert login, "No login provided."
                        res_users = request.env['res.users']
                        get_email = res_users.sudo().check_dp_reset_password(login)
                        if get_email:
                            qcontext['reset_message'] = _(get_email)
                        else:
                            qcontext['error'] = _("Reset password: invalid username or email")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = e.message or e.name
        return request.render('auth_signup.reset_password', qcontext)

    @http.route("/page/confirm_chandler", auth="user", type="http", website=True)
    def chandler_confirm_page(self, *args, **kw):
        """This method used to help add more than one chandler in shipmaster profile."""
        qcontext = request.params.copy()
        user_response = self.check_dp_chandler_confirm_limit(qcontext)
        if user_response.get("found_chandler", False):
            qcontext['error'] = "You already have chandler in your preferred list."
            return request.render("dp_auth.chandler_confirm_template", qcontext)
        if request.httprequest.method == 'POST':
            if user_response.has_key('tot_chandler'):
                if user_response.get('tot_chandler') >= 3:
                    qcontext["primary"] = "You are a registered user in the system and have registered up to 3\
                    preferred Chandlers. Do you wish change one of your preferred Chandlers?"
                else:
                    user = request.env['res.users'].sudo().search([('id', '=', request.session.uid)])
                    if user:
                        tot_chandler = len([c.id for c in user.partner_id.chandler_list_for_shipmaster]) + 1
                        request.env['dp.chandler.partner'].sudo().create({'priority': tot_chandler,
                           'shipmaster_id': user.partner_id.id,
                           'chandler_id': user_response.get("inv_obj").user_id.partner_id.id}).send_mail_to_chandler()
                        qcontext['success'] = "Successfully added preferred chandler in your profile."
                        user_response.get("inv_obj").write({'state':'accepted'})
                    else:
                        qcontext["error"] = "Invalid request."
            else:
                qcontext["error"] = "Invalid request."
        elif qcontext.get("inv_id", False):
            if user_response.has_key('tot_chandler'):
                if user_response.get('tot_chandler') >= 3:
                    qcontext["primary"] = "You are a registered user in the system and have registered up to 3\
                    preferred Chandlers. Do you wish change one of your preferred Chandlers?"
                else:
                    qcontext["info"] = "You are a registered user in the system. Do you want to register Chandler {}\
                     as one of your preferred Chandler?".format(user_response['inv_obj'].user_id.name)
            else:
                qcontext["error"] = "Invalid request."
        else:
            qcontext["error"] = "Invalid Request."
        return request.render("dp_auth.chandler_confirm_template", qcontext)

    def find_duplicate_chandler(self, chandlers):
        """This method helps to find duplicate chandler list in signup page."""
        dub_chandler = []
        chandlers.sort()
        for i in range(len(chandlers) - 1):
            if chandlers[i] == chandlers[i + 1]:
                dub_chandler.append(chandlers[i])
        return dub_chandler

    def check_dp_chandler_limit(self, vals):
        """ This method checking invited existing shipmaster profile having chandler or not."""
        dict_vals = {}
        user_obj = request.env['res.users']
        inv_obj = request.env["dp.shipmaster.invitation"]
        inv_id = inv_obj.sudo().search([('name', '=', vals.get("inv_id")), ('state', '=', 'sent')])
        try:
            if inv_id:
                user_id = user_obj.sudo().search([('login', '=', inv_id.shipmaster_email)])
                if user_id:
                    if user_id.has_group('dp_common.group_shipmaster'):
                        tot_chandler = len([c.id for c in user_id.partner_id.chandler_list_for_shipmaster])
                        dict_vals.update(tot_chandlers=tot_chandler, user_found="Yes")
                else:
                    dict_vals.update(tot_chandlers=0, pc_one=inv_id.user_id.partner_id.name, login=inv_id.shipmaster_email,
                                     inv_id=vals.get("inv_id", False), name=inv_id.shipmaster_name, user_found="No")
        except Exception as e:
            _logger.error(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('check_dp_chandler_limit --------------------------------------------------------------------')
        return dict_vals

    def check_dp_chandler_confirm_limit(self, vals):
        """ This method checking invited existing shipmaster profile having chandler or not."""
        dict_vals = {}
        user_obj = request.env['res.users']
        inv_obj = request.env["dp.shipmaster.invitation"]
        inv_id = inv_obj.sudo().search([('name', '=', vals.get("inv_id")), ('state', '=', 'sent')])
        try:
            if inv_id:
                user_id = user_obj.sudo().search([('id', '=', request.session.uid), ('login', '=', inv_id.shipmaster_email)])
                if user_id:
                    if user_id.has_group('dp_common.group_shipmaster'):
                        found_chandler = False
                        for chdlr in user_id.partner_id.chandler_list_for_shipmaster:
                            if chdlr.chandler_id.id == inv_id.user_id.partner_id.id:
                                found_chandler = True
                                break
                        tot_chandler = len([c.id for c in user_id.partner_id.chandler_list_for_shipmaster])
                        dict_vals.update(tot_chandler = tot_chandler, pc_one=inv_id.user_id.partner_id.name,
                                         login=inv_id.shipmaster_email, inv_id=inv_id.id, name=inv_id.shipmaster_name,
                                         found_chandler=found_chandler, inv_obj=inv_id)
        except Exception as e:
            _logger.error(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno))
            _logger.error('check_dp_chandler_confirm_limit ------------------------------------------------------------')
        return dict_vals

    def check_dp_chandler_user_by_name(self, vals):
        """ This method checking provided name is chandler profile or not """
        status = {'status': False, 'id': False}
        if vals:
            user_id = request.env['res.users'].sudo().search([('partner_id.name', '=', vals)])
            if not user_id:
                return status
            for user in user_id:
                if user.has_group('dp_common.group_chandler'):
                    status['status'] = True
                    status['id'] = user.partner_id.id
                    status['user_obj'] = user
        return status

    def get_required_signup_values(self, qcontext):
        """Exclude this logic from default method"""
        if 'signup' in request.httprequest.path:
            # if(qcontext.get('vessel_name') == 'CREATE AND EDIT..'):
            #     return dict((key, qcontext.get(key)) for key in ('login', 'name', 'password', 'vessel_name',
            #                                                      'create_vessel_nrt','create_vessel_name', 'create_vessel_flag',
            #                                                      'create_vessel_crew','imo', 'phone', 'new_vessel',
            #                                                      'vessel_id', 'call_sign', 'pc_one', 'pc_two',
            #                                                      'pc_three', 'inv_id'))
            # else:
                return dict((key, qcontext.get(key)) for key in ('login', 'name', 'password', 'vessel_name', 'imo', 'phone',
                                                                   'vessel_id', 'call_sign', 'pc_one', 'pc_two', 'new_vessel',
                                                                   'pc_three', 'inv_id'))
        else:
            return qcontext

    def do_signup(self, qcontext):
        """Override the default method."""
        values = self.get_required_signup_values(qcontext)
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.cr.commit()

    def _signup_with_values(self, token, values):
        """Override the default method."""
        user_obj = request.env['res.users']
        db, login, password = user_obj.sudo().signup(values, token)
        request.cr.commit()
        uid = request.session.authenticate(db, login, password)
        if not uid:
            raise SignupError(_('Authentification Failed.'))
        # if not token:
        self.update_user_profile(uid, values)

    def update_user_profile(self, uid, values):
        """First time signup shipmaster data add in user profile."""
        user_obj = request.env['res.users']
        user_id = user_obj.sudo().search([('id', '=', uid)])
        chandler_list = []
        partner_obj = request.env['res.partner']
        first_chandler = False

        if values.get("pc_one", False):
            chandler_id = self.check_dp_chandler_user_by_name(values.get('pc_one'))
            if chandler_id.get("id", False):
                chandler_list.append(
                    [0, False, {'shipmaster_id': user_id.partner_id.id, 'chandler_id': chandler_id['id']}])
                first_chandler = chandler_id['user_obj'].id

        if values.get("pc_two", False):
            chandler_id = self.check_dp_chandler_user_by_name(values.get('pc_two'))
            if chandler_id.get("id", False):
                chandler_list.append([0, False, {'shipmaster_id': user_id.partner_id.id, 'priority': 2,
                                                 'chandler_id': chandler_id['id']}])

        if values.get("pc_three", False):
            chandler_id = self.check_dp_chandler_user_by_name(values.get('pc_three'))
            if chandler_id.get("id", False):
                chandler_list.append([0, False, {'shipmaster_id': user_id.partner_id.id, 'priority': 3,
                                                 'chandler_id': chandler_id['id']}])
        # vessel_type = request.env["vessel.type"].search([('id', '=', values.get('vessel_id'))]).name
        # # store vessel name created from checkout page (request form)
        # if values.get('vessel_name', False) == 'CREATE AND EDIT..':
        #     # create new shipping agent
        #     vessel_name = values.get('create_vessel_name', False)
        #     imo_number = values.get('imo', False)
        #     vessel_id = values.get('vessel_id', False)
        #     vessel_nrt = values.get('create_vessel_nrt', False)
        #     vessel_flag = values.get('create_vessel_flag', False)
        #     vessel_crew = values.get('create_vessel_crew', False)
        #     # shipping_agent_id = values.get('create_shipping_agent_id', False)
        #     try:
        #         if vessel_name and imo_number and vessel_id and vessel_nrt and vessel_flag and vessel_crew:
        #             vessel_name_env = request.env['vessel.name']
        #
        #             existing = vessel_name_env.search(
        #                 [('name', '=', vessel_name), ('imo_number', '=', imo_number), ('type', '=', vessel_id),
        #                  ('nrt', '=', vessel_nrt), ('flag', '=', vessel_flag), ('crew', '=', vessel_crew),
        #                  # ('shipping_agent', '=', shipping_agent_id)
        #                  ])
        #             if not existing.exists():
        #                 new_vessel_name = vessel_name_env.sudo().create({'name': vessel_name, 'imo_number': imo_number,
        #                                                                  'type': vessel_id, 'nrt': vessel_nrt,
        #                                                                  'flag': vessel_flag,
        #                                                                  'crew': vessel_crew,
        #                                                                  # 'shipping_agent': shipping_agent_id
        #                                                                  })
        #             else:
        #                 new_vessel_name = existing
        #         else:
        #             _logger.error('unable to create vessel name!')
        #             raise Exception
        #
        #         if new_vessel_name.exists():
        #             user_id.partner_id.sudo().write({'chandler_list_for_shipmaster': chandler_list,
        #                                              'vessel_name': new_vessel_name.name,
        #                                              'vessel_type': vessel_type,
        #                                              'imo_number': values.get('imo', False),
        #                                              'call_sign': values.get('call_sign', False),
        #                                              'phone': values.get('phone', False),
        #                                              'customer': True})
        #         else:
        #             _logger.error('new_vessel_name does not exist!!')
        #             raise Exception
        #
        #     except Exception as e:
        #         exc_type, exc_obj, exc_tb = sys.exc_info()
        #         _logger.error('Exception Type: ' + str(exc_type))
        #         _logger.error('Exception Error Description: ' + str(exc_obj))
        #         _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(
        #             exc_tb.tb_frame.f_code.co_filename))
        #         _logger.error('unable to create new vessel name!')
        # else:
        #     vess_obj = request.env["vessel.name"].search([('name', '=', values.get('vessel_name').upper())])
            #  _   _     _                        _                         _   _
            # | |_| |__ (_)___   _ __   __ _ _ __| |_   _ __   ___  ___  __| | | |_ ___
            # | __| '_ \| / __| | '_ \ / _` | '__| __| | '_ \ / _ \/ _ \/ _` | | __/ _ \
            # | |_| | | | \__ \ | |_) | (_| | |  | |_  | | | |  __/  __/ (_| | | || (_) |
            #  \__|_| |_|_|___/ | .__/ \__,_|_|   \__| |_| |_|\___|\___|\__,_|  \__\___/
            #                   |_|
            #             _
            #   ___ _ __ | |__   __ _ _ __   ___ ___
            #  / _ \ '_ \| '_ \ / _` | '_ \ / __/ _ \
            # |  __/ | | | | | | (_| | | | | (_|  __/
            #  \___|_| |_|_| |_|\__,_|_| |_|\___\___|
            #
            # this part need to enhance
            # try:
            #     assert len(vess_obj) == 1
            #     vessel_name = vess_obj.name
            # except:
            #     vessel_name = vess_obj[0].name
            # if values.get('new_vessel', False):
            #     if int(values['new_vessel']):
            #         vess_obj.write({'create_uid': user_id.id, 'write_uid': user_id.id})
        user_id.partner_id.sudo().write({'chandler_list_for_shipmaster': chandler_list,
                           # 'vessel_name': vessel_name,
                           # 'vessel_type': vessel_type,
                           # 'imo_number': values.get('imo', False),
                           # 'call_sign': values.get('call_sign', False),
                           'phone': values.get('phone', False),
                           'customer': True})

        latest_shipmaster_data = partner_obj.sudo().search([('id', '=', user_id.partner_id.id)])

        inv_obj = request.env["dp.shipmaster.invitation"]

        inv_id = inv_obj.sudo().search([('name', '=', values.get('inv_id')), ('state', '=', 'sent'), ('user_id', '=', first_chandler)])

        if inv_id:
            inv_id.write({'state': 'accepted'})

        # for chandler in latest_shipmaster_data.chandler_list_for_shipmaster:
        #     chandler.send_mail_to_chandler()

    @http.route(['/create_new_vessel_name'],  type='json',  methods=['POST','GET'], auth="public")
    def create_new_vessel_name(self, **post):
        if request.context.get('open_vessel_form', False):
            # x = request.context['vessel_name']
            return request.env.ref('dp_auth.create_new_vessel').render({'vessel_obj': request.env['vessel.type'].sudo().search([], order='name'),
                                                                        'vessel_name': request.context['vessel_name'].upper(),
                                                                        'vessel_type': request.context['vessel_type']})

        if post:
            """
            {'imo_number': '123321',
             'vessel_crew': '5',
             'vessel_flag': 'sg',
             'vessel_type_id': '364', // vessel type id 
             'vessel_name': 'ahhaha',
             'vessel_nrt': '3'}
            """
            try:
                if not(post.has_key('imo_number') and post.has_key('vessel_flag') and post.has_key('vessel_type_id') and post.has_key('vessel_name')):
                    raise Exception
                vessel_obj = request.env['vessel.name'].search([('name', '=', post.get('vessel_name')),
                                                                ('imo_number', '=', post.get('imo_number')),
                                                                ('flag', '=', post.get('vessel_flag')),
                                                                ('type', '=', int(post.get('vessel_type_id')))])
                if vessel_obj.exists():
                    raise Exception
                request.env['vessel.name'].create({'name': post.get('vessel_name'),
                                                 'type': int(post.get('vessel_type_id')),
                                                 'imo_number': post.get('imo_number'),
                                                 'nrt': post.get('vessel_nrt', None),
                                                 'flag': post.get('vessel_flag'),
                                                 'crew': post.get('vessel_crew', None)})
                # request.session.update('vessel_name': vessel_name})
                return True
                # return request.env.ref('dp_auth.create_new_vessel').render({'success': True,
                #                                                             'vessel_name': vessel_name})
            except Exception:
                return False

    @http.route('/get_chandler_data', type="json", methods=['POST','GET'], auth="public")
    def get_port_list(self, **kwargs):
        rtn_dict = {}
        if kwargs.has_key('vessel_name'):
            vessel_obj = request.env['vessel.name'].search([('name', '=', kwargs.get('vessel_name'))], order='name')
            rtn_dict = {"vessel_type": vessel_obj.type.id or '', 'imo_number': vessel_obj.imo_number or '', "vessel_type_name": vessel_obj.type.name or ''}
        return json.dumps(rtn_dict)