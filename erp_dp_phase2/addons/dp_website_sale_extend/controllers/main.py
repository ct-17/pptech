import logging, sys
import werkzeug
from datetime import datetime
from openerp.exceptions import ValidationError
from openerp import tools, http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.exceptions import except_orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DSDF

from datetime import datetime as dt
from multiprocessing import cpu_count
import threading
CPU = min(cpu_count(), 16)
import json
_logger = logging.getLogger('DPwebsite_sale')







class DPwebsite_sale_extend(website_sale):

    def checkout_values(self, data=None):
        res = super(DPwebsite_sale_extend, self).checkout_values(data)
        # check if confirm has been pressed
        confirm = False
        if not res.get('rec_cache', False):
            res['rec_cache'] = {'rec_chan_name1': request.session.get('rec_chan_name1', None),
                                'rec_chan_email1': request.session.get('rec_chan_email1', None),
                                'rec_chan_name2': request.session.get('rec_chan_name2', None),
                                'rec_chan_email2': request.session.get('rec_chan_email2', None),
                                'rec_chan_name3': request.session.get('rec_chan_name3', None),
                                'rec_chan_email3': request.session.get('rec_chan_email3', None),
                                }

        # chandlers_obj = request.env['res.partner'].sudo().search([('supplier', '=', True)])
        chandlers_obj = request.env['dp.chandler.temp'].sudo().search([('active', '=', True)])
        vessel_obj = request.env['vessel.type'].search([])
        vessel_name_obj = request.env['vessel.name'].search([])
        shipping_obj = request.env['shipping.agent'].sudo().search([('active', '=', True)], order='name')
        port_obj = request.env['custom.port'].sudo().search([])
        user_id = request.env['res.users'].sudo().browse(request.uid)
        preferred_chandlers_obj = user_id.partner_id.sudo().chandler_list_for_shipmaster
        if res.has_key('checkout'):
            i = 1
            for pref_chan in preferred_chandlers_obj:
                pref_chan_id = request.env['dp.chandler.temp'].sudo().search(
                    [('partner_id', '=', pref_chan.chandler_id.id), ('state', '=', 'approved')]) or request.env[
                                   'dp.chandler.temp']
                res['checkout']['pref_chan%d' % i] = pref_chan.chandler_id.name
                res['checkout']['pref_chan%d_id' % i] = pref_chan_id.id
                i += 1
            # res['checkout']['vessel_name'] = user_id.partner_id.vessel_name or None
            # res['checkout']['vessel_type'] = user_id.partner_id.vessel_type or None
            # res['checkout']['imo_number'] = user_id.partner_id.imo_number or None
            # res['checkout']['call_sign'] = user_id.partner_id.call_sign or None

            sale_id = ''
            if request.session.has_key('sale_order_id') or request.session.has_key('sale_last_order_id'):
                sale_id = request.session.get('sale_order_id', False)
            if sale_id == '' or sale_id is False:
                sale_id = request.session.get('sale_last_order_id', False)
            if sale_id == '' or sale_id is False:
                raise except_orm(_('Unable to retrieve sale id'),
                                 _('Please contact system admin regarding this issue!'))

            sale_obj = request.env['sale.order'].sudo().browse(sale_id)
            res['checkout']['date_order'] = dt.strptime(sale_obj.date_order, DSDF).strftime('%d/%m/%Y')
            if sale_obj.estimated_arrival and sale_obj.shipping_agent_id:
                draft_date = datetime.strptime(sale_obj.estimated_arrival, '%Y-%m-%d')
                res['checkout']['estimated_arrival'] = draft_date.strftime("%d/%m/%Y")
                res['checkout']['shipping_agent_id'] = sale_obj.shipping_agent_id.name
            if sale_obj.estimated_departure:
                draft_date = datetime.strptime(sale_obj.estimated_departure, '%Y-%m-%d')
                res['checkout']['estimated_departure'] = draft_date.strftime("%d/%m/%Y")
            if sale_obj.next_port_id:
                res['checkout']['next_port_id'] = sale_obj.next_port_id
            if sale_obj.last_port_id:
                res['checkout']['last_port_id'] = sale_obj.last_port_id
            if sale_obj.order_contact_person:
                res['checkout']['order_contact_person'] = sale_obj.order_contact_person
            if sale_obj.po_num:
                res['checkout']['po_num'] = sale_obj.po_num
            if sale_obj.marking_num:
                res['checkout']['marking_num'] = sale_obj.marking_num
            if sale_obj.order_remarks:
                res['checkout']['order_remarks'] = sale_obj.order_remarks
            if sale_obj.vessel_name:
                res['checkout']['vessel_name'] = sale_obj.vessel_name.name
            if sale_obj.other_shipping_agent:
                res['checkout']['other_shipping_agent'] = sale_obj.other_shipping_agent
            if sale_obj.other_vessel_name:
                res['checkout']['other_vessel_name'] = sale_obj.other_vessel_name
            if sale_obj.order_mobile_number:
                res['checkout']['order_mobile_number'] = sale_obj.order_mobile_number

            seq = 1
            for chan in sale_obj.many_chandler:
                if chan.chandler.state == 'draft':
                    res['checkout']['rec_chan_name{}'.format(str(seq))] = chan.chandler.name
                    res['checkout']['rec_chan_email{}'.format(str(seq))] = chan.chandler.email
                    seq += 1

            for seq in range(1, 4):
                if not res['checkout'].has_key('rec_chan_name{}'.format(str(seq))):
                    res['checkout']['rec_chan_name{}'.format(str(seq))] = ''
                    res['checkout']['rec_chan_email{}'.format(str(seq))] = ''

            if data:
                res['checkout']['order_contact_person'] = data.get('order_contact_person', "")
                res['checkout']['order_mobile_number'] = data.get('order_mobile_number', "")
                res['checkout']['po_num'] = data.get('po_num', "")
                res['checkout']['marking_num'] = data.get('marking_num', "")
                res['checkout']['order_remarks'] = data.get('remarks', "")
                res['checkout']['estimated_arrival'] = data.get('estimated_arrival', "")
                res['checkout']['last_port_id'] = data.get('last_port_id', "")
                res['checkout']['next_port_id'] = data.get('next_port_id', "")
                res['checkout']['stay_duration'] = data.get('stay_duration', "")
                res['checkout']['vessel_id'] = data.get('vessel_id', False)
                res['checkout']['vessel_name'] = data.get('vessel_name', "")
                if data.get('vessel_name', False):
                    if data.get('vessel_name').upper() == request.env.ref('dp_base_extend.default_others_vessel_name').name.upper():
                        res['checkout']['other_vessel_name'] = data.get('other_vessel_name', "")
                    else:
                        res['checkout']['other_vessel_name'] = ''
                        data.update(other_vessel_name='')
                res['checkout']['call_sign'] = data.get('call_sign', "")
                res['checkout']['imo_number'] = data.get('imo_number', "")
                res['checkout']['estimated_departure'] = data.get('estimated_departure', "")
                if data.get('shipping_agent_id', False):
                    res['checkout']['shipping_agent_id'] = request.env['shipping.agent'].sudo().search([('name', '=', data.get('shipping_agent_id'))]).id
                    if res['checkout']['shipping_agent_id']:
                        data['shipping_agent_id'] = res['checkout']['shipping_agent_id']
                    else:
                        res['checkout'].update({
                            'shipping_agent_id': 'error',
                            'false_shipping_agent_id': data.get('shipping_agent_id')
                        })
                        data.update(shipping_agent_id = '')
                else:
                    res['checkout']['shipping_agent_id'] = False
                if isinstance(data.get('shipping_agent_id'), int):
                    if request.env['shipping.agent'].sudo().browse(data.get('shipping_agent_id')):
                        if request.env['shipping.agent'].sudo().browse(data.get('shipping_agent_id')).name.upper() == \
                                request.env.ref('dp_base_extend.default_others_shipping_agent').name.upper():
                            res['checkout']['other_shipping_agent'] = data.get('other_shipping_agent', "")
                        else:
                            res['checkout']['other_shipping_agent'] = ''
                            data.update(other_shipping_agent='')

                res['checkout']['create_vessel_name'] = data.get('create_vessel_name', "")
                res['checkout']['create_imo_number'] = data.get('create_imo_number', "")
                res['checkout']['create_vessel_id'] = data.get('create_vessel_id', False)
                res['checkout']['create_vessel_nrt'] = data.get('create_vessel_nrt', "")
                res['checkout']['create_vessel_flag'] = data.get('create_vessel_flag', "")
                res['checkout']['create_vessel_crew'] = data.get('create_vessel_crew', "")
                # res['checkout']['create_shipping_agent_id'] = data.get('create_shipping_agent_id', False)
                res['checkout']['submit_btn1_count'] = '0'
                res['checkout']['submit_btn2_count'] = '0'
                res['checkout']['submit_btn3_count'] = '0'
                res['checkout']['vessel_type'] = data.get('vessel_type', False)
                # res['checkout']['rec_chan_name1'] = data.get('recommend_chandler_name1', '')
                # res['checkout']['rec_chan_email1'] = data.get('recommend_chandler_email1', '')
                # res['checkout']['rec_chan_name2'] = data.get('recommend_chandler_name2', '')
                # res['checkout']['rec_chan_email2'] = data.get('recommend_chandler_email2', '')
                # res['checkout']['rec_chan_name3'] = data.get('recommend_chandler_name3', '')
                # res['checkout']['rec_chan_email3'] = data.get('recommend_chandler_email3', '')

        else:
            for i in range(1, 4):
                res['checkout']['pref_chan%d' % i] = "Chandler #{}".format(i)
                res['checkout']['pref_chan%d_id' % i] = "{}".format(None)
        res['chandlers1'] = chandlers_obj
        res['chandlers2'] = chandlers_obj
        res['chandlers3'] = chandlers_obj
        res['vessel_name_obj'] = vessel_name_obj
        res['vessel_obj'] = vessel_obj
        res['shipping_obj'] = shipping_obj
        res['next_port_obj'] = port_obj
        res['last_port_obj'] = port_obj

        if data:
            # data is not None when user click confirm on /shop/checkout
            """ SAMPLE
            data = 
            {
             'chandler_autocomplete_input1': u'chandler1', 'chandler_checkbox1_name': u'on',
             'chandler_autocomplete_input2': u'chandler3', 'chandler_checkbox2_name': u'on',
             'chandler_autocomplete_input3': u'chandler4', 'chandler_checkbox3_name': u'on',

             'recommend_chandler_email1': u'chinsheng.soh@pptech.com.sg', 'recommend_chandler_name1': u'cs3',
             'recommend_chandler_email2': u'chinsheng.soh@pptech.com.sg', 'recommend_chandler_name2': u'cs4',
             'recommend_chandler_email3': u'chinsheng.soh@pptech.com.sg', 'recommend_chandler_name3': u'cs5',

             'last_port': u'', 'next_port': u'',
             'name': u'shipmaster', 'phone': u'shipmastrer41@pptech.com.sg', 
             'email': u'shipmastrer41@pptech.com.sg',
             'estimated_arrival': u'', 'stay_duration': u'2',
             'street': u'1234567', 'street2': u'callsign', 'zip': u'ship'

             'vessel_id': u'1',            

             'shipping_agent_name': u'', 'shipping_agent_cr_number': u'', 'shipping_agent_contact': u'',
             'shipping_id': u'0', 'shipping_agent_id': u'',

             }

            """
            confirm = bool(data.get('check_confirm_before_cache', False))
            request.session.update({'rec_chan_name1': data.get('recommend_chandler_name1', None)})
            request.session.update({'rec_chan_email1': data.get('recommend_chandler_email1', None)})
            request.session.update({'rec_chan_name2': data.get('recommend_chandler_name2', None)})
            request.session.update({'rec_chan_email2': data.get('recommend_chandler_email2', None)})
            request.session.update({'rec_chan_name3': data.get('recommend_chandler_name3', None)})
            request.session.update({'rec_chan_email3': data.get('recommend_chandler_email3', None)})

            sale_id = request.session.get('sale_order_id', False)
            if not sale_id:
                sale_id = request.session.get('sale_last_order_id', False)
            if not sale_id:
                raise except_orm(_('Unable to retrieve sale order id'), _('Please contact system administrator!'))
            sale_order = request.env['sale.order'].browse(sale_id)
            if data.get('vessel_name', False):
                if request.env["vessel.name"].search([("name", "=", data.get('vessel_name', None))]):
                    vessel_name = request.env["vessel.name"].search([("name", "=", data.get('vessel_name', None))])[0].id
                else:
                    vessel_name = ''
                    res['checkout'].update({
                        'vessel_name': 'error',
                        'false_vessel_name': data.get('vessel_name')
                    })
                    # data.update(vessel_name='error')
            else:
                vessel_name = ''
            if request.env["vessel.type"].search([("name", "=", data.get('vessel_type', None))]):
                vessel_type = request.env["vessel.type"].search([("name", "=", data.get('vessel_type', None))])[0].id
            else:
                vessel_type = ''
            order_data = {
                'last_port_id': data.get('last_port_id', None),
                'next_port_id': data.get('next_port_id', None),
                'stay_duration': data.get('stay_duration', None),
                'vessel_id': vessel_type,
                'vessel_name': vessel_name,
                "call_sign": data.get("call_sign", None),
                "imo_number": data.get("imo_number", None),
                'shipping_agent_id': data.get('shipping_agent_id', None),
                'other_vessel_name': data.get('other_vessel_name', None),
                'other_shipping_agent': data.get('other_shipping_agent', None),
                'po_num': data.get('po_num', None),
                'marking_num': data.get('marking_num', None),
                'order_remarks': data.get('remarks', None),
                'order_contact_person': data.get('order_contact_person', None),
                'order_mobile_number': data.get('order_mobile_number', None),
            }
            try:
                eta = dt.strptime(data.get('estimated_arrival', ), '%d/%m/%Y') if data.get('estimated_arrival',
                                                                                           "") else False
            except:
                eta = None

            try:
                etd = dt.strptime(data.get('estimated_departure', ), '%d/%m/%Y') if data.get('estimated_departure',
                                                                                             "") else False
            except:
                etd = None
            order_data.update({'estimated_arrival': eta})
            order_data.update({'estimated_departure': etd})

            last_port, next_port = None, None
            if data.get('last_port_id', False):
                port_code, port_name = data.get('last_port_id').split(':')
                last_port = request.env['custom.port'].sudo().search(
                    [('code', '=', port_code), ('name', '=', port_name[1:])]).id or False

            if data.get('next_port_id', False):
                try:
                    port_code, port_name = data.get('next_port_id').split(':')
                    next_port = request.env['custom.port'].sudo().search(
                        [('code', '=', port_code), ('name', '=', port_name[1:])]) or False
                    res['checkout'].update({
                        'next_port_id': next_port,
                    })
                except:
                    res['checkout'].update({
                             'next_port_id': 'error',
                             'false_next_port_id': data.get('next_port_id')
                        })
            order_data.update({
                'last_port_id': last_port,
                'next_port_id': next_port.id if next_port else False,
            })


            skip_create_ship_agent = False
            # if confirm:
            #     if data.get('shipping_agent_id', False) == 'CREATE..' and \
            #             data.get('shipping_agent_name_cache', False) == data.get('shipping_agent_name', False) and \
            #             data.get('shipping_agent_cr_num_cache', False) == data.get('shipping_agent_cr_number',
            #                                                                        False) and \
            #             data.get('shipping_agent_contact_cache', False) == data.get('shipping_agent_contact', False):
            #         skip_create_ship_agent = True
            # if data.get('shipping_agent_id', False) == 'CREATE..':
            #     # create new shipping agent
            #     contact = data.get('shipping_agent_contact', False)
            #     cr_num = data.get('shipping_agent_cr_number', False)
            #     name = data.get('shipping_agent_name', False)
            #     try:
            #         if contact and cr_num and name:
            #             name = name.upper()
            #             ship_agent_env = request.env['shipping.agent']
            #
            #             existing = ship_agent_env.search(
            #                 [('name', '=', name), ('crNum', '=', cr_num), ('contact', '=', contact)])
            #             if not existing.exists():
            #                 new_ship_agent = ship_agent_env.sudo().create({'name': name, 'crNum': cr_num,
            #                                                                'contact': contact, 'active': True})
            #             else:
            #                 new_ship_agent = existing
            #         else:
            #             _logger.error('unable to create shipping agent!!')
            #             raise Exception
            #
            #         if new_ship_agent.exists():
            #             order_data.update({'shipping_agent_id': new_ship_agent.id})
            #             new_shipping_agent_id = request.env['shipping.agent'].search([('name', '=', name.upper())])
            #             res['checkout']['shipping_agent_id'] = new_shipping_agent_id
            #         else:
            #             _logger.error('new_ship_agent does not exist!!')
            #             raise Exception
            #
            #     except Exception as e:
            #         exc_type, exc_obj, exc_tb = sys.exc_info()
            #         _logger.error('Exception Type: ' + str(exc_type))
            #         _logger.error('Exception Error Description: ' + str(exc_obj))
            #         _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(
            #             exc_tb.tb_frame.f_code.co_filename))
            #         _logger.error('unable to create new shipping agent!')
            #
            # else:
            #     order_data.update({'shipping_agent_id': data.get('shipping_agent_id', False)})

            if order_data['estimated_arrival'] == '':
                order_data['estimated_arrival'] = None

            sale_order.sudo().with_context({'need_recompute_discount': True}).write(order_data)

            #  _____      _     _   _
            # | ____|_  _(_)___| |_(_)_ __   __ _
            # |  _| \ \/ / / __| __| | '_ \ / _` |
            # | |___ >  <| \__ \ |_| | | | | (_| |
            # |_____/_/\_\_|___/\__|_|_| |_|\__, |
            #                               |___/
            #   ____ _                     _ _
            #  / ___| |__   __ _ _ __   __| | | ___ _ __ ___
            # | |   | '_ \ / _` | '_ \ / _` | |/ _ \ '__/ __|
            # | |___| | | | (_| | | | | (_| | |  __/ |  \__ \
            #  \____|_| |_|\__,_|_| |_|\__,_|_|\___|_|  |___/
            chan_env = request.env['dp.chandler.temp']
            soc_env = request.env['sale.order.chandler']
            if sale_order.sudo().many_chandler.exists():
                sale_order.sudo().many_chandler.unlink()
            chan_on = [data.get('chandler_checkbox1_name', False), data.get('chandler_checkbox2_name', False),
                       data.get('chandler_checkbox3_name', False)]
            chan_list = [data.get('chandler_autocomplete_input%s' % str(i + 1)) for i in range(len(chan_on)) if
                         chan_on[i]]
            chandlers = chan_env.search([('name', 'in', chan_list), ('state', '=', 'approved')])
            res['checkout']['chandlers'] = chandlers
            try:
                assert len(chan_list) == len(chandlers)
            except AssertionError as ae:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                _logger.error('Exception Type: ' + str(exc_type))
                _logger.error('Exception Error Description: ' + str(exc_obj))
                _logger.error(
                    'Line Numnber: ' + str(exc_tb.tb_lineno) + 'Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
                _logger.error('Possible of duplicate chandlers found')

            chan_admin = chan_env.get_one_chandler_admin()
            seq = 0
            for chan in chandlers:
                seq = chan_list.index(chandlers[0].name) + 1
                soc_env.sudo().create({
                    'chandler': chan.id,
                    'seq': seq,
                    'active': True,
                    'order_id': sale_order.id
                })

            #  ____                                                   _
            # |  _ \ ___  ___ ___  _ __ ___  _ __ ___   ___ _ __   __| |
            # | |_) / _ \/ __/ _ \| '_ ` _ \| '_ ` _ \ / _ \ '_ \ / _` |
            # |  _ <  __/ (_| (_) | | | | | | | | | | |  __/ | | | (_| |
            # |_| \_\___|\___\___/|_| |_| |_|_| |_| |_|\___|_| |_|\__,_|
            #
            #   ____ _                     _ _
            #  / ___| |__   __ _ _ __   __| | | ___ _ __ ___
            # | |   | '_ \ / _` | '_ \ / _` | |/ _ \ '__/ __|
            # | |___| | | | (_| | | | | (_| | |  __/ |  \__ \
            #  \____|_| |_|\__,_|_| |_|\__,_|_|\___|_|  |___/
            skipper = {1: False, 2: False, 3: False}
            if data:
                if data.get('recommend_chandler_name1_cache', False) == data.get('recommend_chandler_name1', False) and \
                        data.get('recommend_chandler_email1_cache', False) == data.get('recommend_chandler_email1',
                                                                                       False):
                    skipper[1] = True
                if data.get('recommend_chandler_name2_cache', False) == data.get('recommend_chandler_name2', False) and \
                        data.get('recommend_chandler_email2_cache', False) == data.get('recommend_chandler_email2',
                                                                                       False):
                    skipper[2] = True
                if data.get('recommend_chandler_name3_cache', False) == data.get('recommend_chandler_name3', False) and \
                        data.get('recommend_chandler_email3_cache', False) == data.get('recommend_chandler_email3',
                                                                                       False):
                    skipper[3] = True
            num_of_loop = [data.get('recommend_chandler_name{}'.format(i), False) for i in range(0, len(data)) if
                           data.get('recommend_chandler_name{}'.format(i), False) is not False]

            def chandler_exist(name):
                dct = request.env['dp.chandler.temp'].sudo().search([('name', '=', name)])
                return dct

            for i in range(len(num_of_loop)):
                name = data.get('recommend_chandler_name{}'.format(i + 1), False)
                if name not in ("", False):
                    if not confirm and not skipper[i + 1]:
                        email = data.get('recommend_chandler_email{}'.format(i + 1), False)
                        existing_chan = chandler_exist(name.strip())
                        if existing_chan.exists():
                            new_chan = existing_chan
                        else:
                            new_chan = chan_env.create(
                                {'name': name.strip(), 'email': email.strip(), 'chandler_priority': i + 1,
                                 'state': 'draft',
                                 'approver_id': chan_admin.partner_id.id})

                        seq += 1
                        soc_env.sudo().create({
                            'chandler': new_chan.id,
                            'seq': seq,
                            'active': True,
                            'order_id': sale_order.id
                        })

        res['cache'] = self.get_empty_cache()
        return res

    # TODO: BinhTT override this function to pending error,
    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        context.update(need_recompute_discount=True)
        order = request.website.sale_get_order(context=context)
        if not order:
            return request.redirect("/shop")

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values(post)

        values["error"] = self.checkout_form_validate(values["checkout"])
        if values.has_key('checkout'):
            if values['checkout'].get('date_order', False) not in ('', False) and values['checkout'].get(
                    'estimated_arrival', False) not in ('', False):
                do = dt.strptime(values['checkout']['date_order'], '%d/%m/%Y')
                try:
                    ea = dt.strptime(values['checkout']['estimated_arrival'], '%d/%m/%Y')
                except:
                    ea = dt.strptime('01/01/1001', '%d/%m/%Y')
                if ea < do:
                    values["error"].update({'estimated_arrival': 'missing'})
                    values["error"].update({'estimated_departure': 'missing'})
        if values["error"]:
            values['cache'] = self.get_sale_order_information(post)
            return request.website.render("website_sale.checkout", values)

        self.checkout_form_save(values["checkout"])

        request.session['sale_last_order_id'] = order.id

        request.website.sale_get_order(update_pricelist=True, context=context)

        return request.redirect("/shop/payment")


    def checkout_form_validate(self, data):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        # Validation
        error = dict()

        if not data.get('order_contact_person', False):
            error["name"] = 'missing'

        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'missing'

        if not data.get('vessel_name', False):
            error["vessel_name"] = 'missing'

        if data.get('vessel_name', '') == 'error':
            error["vessel_name"] = 'missing'

        if data.get('vessel_name', False) == 'OTHERS':
            if not data.get('other_vessel_name', False):
                error["other_vessel_name"] = 'missing'

        if not data.get('order_mobile_number', False):
            error["order_mobile_number"] = 'missing'

        # if data.get('vessel_name') == 'CREATE AND EDIT..':
        #     if not data.get('create_vessel_name', False):
        #         error["vessel_name"] = 'missing'
        #     if not data.get('create_imo_number', False):
        #         error["vessel_name"] = 'missing'
        #     if (not data.get('create_vessel_id', False)) or data.get('create_vessel_id') == 'Vessel Type..':
        #         error["vessel_name"] = 'missing'
        #     if not data.get('create_vessel_nrt', False):
        #         error["vessel_name"] = 'missing'
        #     if not data.get('create_vessel_flag', False):
        #         error["vessel_name"] = 'missing'
        #     if not data.get('create_vessel_crew', False):
        #         error["vessel_name"] = 'missing'
        if data.get('next_port_id', '') == 'error':
            error["next_port_id"] = 'missing'
        # if not data.get('vessel_type', False):
        #     error["vessel_type"] = 'missing'

        if not data.get('shipping_agent_id', False):
            error["shipping_agent_id"] = 'missing'

        if data.get('shipping_agent_id', '') == 'error':
            error["shipping_agent_id"] = 'missing'

        if isinstance(data.get('shipping_agent_id', False), int):
            if request.env['shipping.agent'].browse(data.get('shipping_agent_id', False)).name == 'OTHERS':
                if not data.get('other_shipping_agent', False):
                    error["other_shipping_agent"] = 'missing'

        if not data.get('chandlers', False):
            error["select_chandlers"] = 'missing'

        if not data.get('estimated_arrival', False):
            error["estimated_arrival"] = 'missing'

        if not data.get('estimated_departure', False):
            error["estimated_departure"] = 'missing'

        return error

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        res = super(DPwebsite_sale_extend, self).product(product, category, search, **kwargs)
        if request.uid == 3:
            if category:
                if request.env['product.public.category'].search([('id','=',category)]).hidden_to_public:
                    return request.website.render("website.403")
            elif product:
                if product.public_categ_ids.hidden_to_public:
                    return request.website.render("website.403")
        return res

    @http.route()
    def shop(self, page=0, category=None, search='', **post):
        res = super(DPwebsite_sale_extend, self).shop(page, category, search, **post)
        if request.session:
            if request.session.sale_order_id is None:
                user_obj = request.env['res.users'].sudo().browse(request.session.uid)
                sale_obj = request.env['sale.order'].sudo().search([('partner_id', '=', user_obj.partner_id.id)], order='id desc', limit=1)
                if sale_obj.state == 'draft' and sale_obj.expire_quote_state == 'active':
                    request.session.sale_order_id = sale_obj.id
        return res

    @http.route(['/create_new_shipping_agent'], type='json', methods=['POST', 'GET'], auth="public")
    def create_new_shipping_agent(self, **post):
        if request.context.get('open_shipping_agent_form', False):
            # x = request.context['vessel_name']
            return request.env.ref('dp_website_sale_extend.create_new_shipping_agent').render(
                {'shipping_agent_name': request.context['shipping_agent_name'].upper()})

        if post:
            try:
                if not (post.has_key('shipping_agent_name')):
                    raise Exception
                shipping_agent_obj = request.env['shipping.agent'].search([('name', '=', post.get('shipping_agent_name'))])
                if shipping_agent_obj.exists():
                    raise Exception
                request.env['shipping.agent'].sudo().create({'name': post.get('shipping_agent_name'),
                                                   'contact': post.get('shipping_agent_contact'),
                                                   'crNum': post.get('shipping_agent_cr_number'),
                                                    'active': True})
                return True
            except Exception:
                return False

    @http.route('/customize_check_login', type="json", auth="public")
    def customize_check_login(self, **kwargs):
        user = request.env['res.users'].browse(request.env.uid)
        public_user = http.request.env['res.users'].sudo().search(
            [('id', '=', 3), ('active', '=', False)])  # Public user default ID
        if user.id == public_user.id:
            return True
        else:
            return False


    @http.route('/myenquiry_cancel_order', method="POST", type="json", auth="public")
    def myenquiry_cancel_order(self, **kwargs):
        """
        {
        'order_id'; 1,
        'order_line_ids': [[2, 10],[3, 0]]
        }
        order_line_ids => [[id, qty],[id, qty], ...]

        :param kwargs:
        :return:
        """
        try:
            sale_id = 0
            if isinstance(kwargs.get('order_id', False), str) or isinstance(kwargs.get('order_id', False), unicode):
                sale_id = int(kwargs.get('order_id'))
            if isinstance(kwargs.get('order_id', False), int):
                sale_id = kwargs.get('order_id', False)
            sale_obj = request.env['sale.order'].browse(sale_id)
            order_line_ids = kwargs.get('order_line_ids', [])
            sale_obj.pre_write_sanitize(order_line_ids)
            return True
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            _logger.error('dp_website_sale_extend.myenquiry_cancel_order exception: {e}'.format(e=e))
            _logger.error('Exception Type: ' + str(exc_type))
            _logger.error('Exception Error Description: ' + str(exc_obj))
            _logger.error('Line Numnber: ' + str(exc_tb.tb_lineno) + ' Filename: ' + str(exc_tb.tb_frame.f_code.co_filename))
        return False