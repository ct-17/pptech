openerp.booking_calendar = function (session) {
    var _t = session.web._t;
    var QWeb = session.web.qweb;
    var DTF = 'YYYY-MM-DD HH:mm:ss';
    var MIN_TIME_SLOT = 1; //hours
    var SLOT_START_DELAY_MINS = 15; // mins

    session.web.BookingCalendar = session.web.Dialog.extend({
        template: "BookingCalendar",
        bookings: [],
        init: function (parent, options, content) {
            this._super(parent, options);
            this.view = options.view;
            this.bookings = [];
            this.resources = [];
        },
        start: function() {
            this.$calendar = this.$('#calendar');
            this.init_calendar();
        },
        set_record: function(id) {
            var self = this;
            this.record_id = id;
            var model = new session.web.Model("resource.resource");
            model.query(['id', 'name'])
                .filter([['to_calendar', '=', true]])
                .all().then(function (resources) {
                    self.$('#external-events').html(QWeb.render("BookingCalendar.resources", { resources : resources }));
                    self.init_ext_events();
                    self.$calendar.fullCalendar24('refetchEvents');
                });
        },
        init_calendar: function() {
            var self = this;
            this.$calendar.fullCalendar24({
                header: {
                  left: 'prev,next today',
                  center: 'title',
                  right: 'month,agendaWeek,agendaDay'
                },
                dropAccept: '.fc-event',
                handleWindowResize: true,
                height: 'auto',
                editable: true,
                droppable: true, // this allows things to be dropped onto the calendar
                eventResourceField: 'resourceId',
                slotDuration: '01:00:00',
                allDayDefault: false,
                allDaySlot: false,
                defaultTimedEventDuration: '01:00:00',
                displayEventTime: false,
                firstDay: 1,
                defaultView: 'month',
                timezone: 'local',
                weekNumbers: true,
                slotEventOverlap: false,
                events: self.load_events,
                eventReceive: self.event_receive,
                eventOverlap: self.event_overlap,
                eventDrop: self.event_drop,
                eventResize: self.event_drop,
                dayClick: self.day_click,
                viewRender: self.view_render,
                dialog: self
            });
        },
        init_ext_events: function() {
            var self = this;
            this.resources = [];
            this.$('#external-events .fc-event').each(function() {
                self.resources.push($(this).data('resource'));
                $(this).data('event', {
                    title: $.trim($(this).text()), // use the element's text as the event title
                    stick: true, // maintain when user navigates (see docs on the renderEvent method)
                    resourceId: $(this).data('resource'),
                    borderColor: 'red',
                    color: $(this).data('color'),
                });
                // make the event draggable using jQuery UI
                $(this).draggable({
                    zIndex: 999,
                    revert: true,      // will cause the event to go back to its
                    revertDuration: 0  //  original position after the drag
                })
                .css('background-color', $(this).data('color'))
                .css('border-color', $(this).data('color'));
            });
        },
        load_events: function(start, end, timezone, callback) {
            var self = this;
            var model = new session.web.Model("sale.order.line");
            model.call('get_bookings', [start.format(DTF), end.format(DTF), self.options.dialog.resources])
                .then(function (events) {
                    for(var i = events.length - 1; i >= 0; i--) {
                        var dialog = self.options.dialog;
                        if(dialog.$calendar.fullCalendar24('clientEvents', events[i].id).length) {
                            events.splice(i, 1);
                        }
                    }
                    callback(events);
                });
        },
        update_record: function(event) {
            var start = event.start.clone();
            var end = event.end ? event.end.clone() : start.clone().add(MIN_TIME_SLOT, 'hours');
            var record = this.view.records.get(this.record_id);
            this.view.start_edition(record, {});
            this.view.editor.form.fields.resource_id.set_value(event.resourceId);
            this.view.editor.form.fields.booking_start.set_value(start.utc().format(DTF));
            this.view.editor.form.fields.booking_end.set_value(end.utc().format(DTF));
        },
        warn: function(text) {
            new session.web.Dialog(this, {
                    title: _t("Warning"), size: 'medium',
                },
                $("<div />").text(text)
            ).open();
        },
        event_receive: function(event, allDay, jsEvent, ui) {
            var dialog = this.opt('dialog');
            if (event.start < moment().add(-SLOT_START_DELAY_MINS, 'minutes')){
                dialog.warn(_t('Please book on time in ' + SLOT_START_DELAY_MINS + ' minutes from now.'));
                dialog.$calendar.fullCalendar24('removeEvents', [event._id]);
                return false;
            }
            dialog.$calendar.fullCalendar24('removeEvents', [dialog.record_id]);
            dialog.update_record(event);
            event._id = dialog.record_id;
            dialog.$calendar.fullCalendar24('updateEvent', event);
        },
        event_drop: function(event, delta, revertFunc, jsEvent, ui, view){
            var dialog = view.options.dialog;
            if (event.start < moment().add(-SLOT_START_DELAY_MINS, 'minutes')){
                dialog.warn(_t('Please book on time in ' + SLOT_START_DELAY_MINS + ' minutes from now.'));
                revertFunc(event);
                return false;
            }
            dialog.update_record(event);
        },
        event_overlap: function(stillEvent, movingEvent) {
            return stillEvent.resourceId != movingEvent.resourceId;
        },
        day_click: function(date, jsEvent, view) {
            if (view.name == 'month' && $(jsEvent.target).hasClass('fc-day-number')) {
                view.calendar.changeView('agendaDay');
                view.calendar.gotoDate(date);
            }
        },
        view_render: function(view, element) {
            // make week names clickable for quick navigation
            if (view.name == 'month') {
                var $td = $(element).find('td.fc-week-number');
                $td.each(function () {
                    var week = parseInt($(this).find('span').text());
                    if (week) {
                        $(this).data('week', week)
                            .css({'cursor': 'pointer'})
                            .find('span').html('&rarr;');
                    }
                });
                $td.click(function(){
                    var week = $(this).data('week');
                    if (week) {
                        var m = moment();
                        m.week(week);
                        if (week < view.start.week()) {
                            m.year(view.end.year());
                        }
                        view.calendar.changeView('agendaWeek');
                        view.calendar.gotoDate(m);
                    }
               });
            } else if (view.name == 'agendaWeek') {
                $(element).find('th.fc-day-header').css({'cursor': 'pointer'})
                    .click(function(){
                        var m = moment($(this).text(), view.calendar.option('dayOfMonthFormat'));
                        if (m < view.start) {
                            m.year(view.end.year());
                        }
                        view.calendar.changeView('agendaDay');
                        view.calendar.gotoDate(m);
                    });
            }
        },
        open: function(id) {
            if (this.dialog_inited) {
                var dialog_inited = true;
            }
            var res = this._super();
            this.set_record(id);
            if (dialog_inited) {
                this.$dialog_box.modal('show');
            }
            return res;
        }
    });


    session.web.form.One2ManyListView.include({
        do_button_action: function (name, id, callback) {
            var self = this;
            if (name == 'open_calendar') {
                if (!self.o2m.bc || self.o2m.bc.isDestroyed()) {
                    self.o2m.bc = new session.web.BookingCalendar(this, {
                        // dialogClass: 'oe_act_window',
                        size: 'large',
                        title: _t('Booking Calendar'),
                        destroy_on_close: false,
                        record_id: id,
                        view: self
                    });
                }
                self.o2m.bc.open(id).on('closing', this, function (e){
                    callback(id);
                });
            } else {
                this._super(name, id, callback);    
            }
        },
    });

    session.web.ListView.List.include({
        init: function (group, opts) {
            var self = this;
            this._super(group, opts);
            this.$current.delegate('.oe_button_calendar', 'click', function (e) {
                e.stopPropagation();
                var $target = $(e.currentTarget),
                    $row = $target.closest('tr'),
                    record_id = self.row_id($row);
                if ($target.attr('disabled')) {
                    return;
                }
                $target.attr('disabled', 'disabled');
                
                $(self).trigger('action', ['open_calendar', record_id, function (id) {
                    $target.removeAttr('disabled');
                    // return self.reload_record(self.records.get(id));
                }]);
            });

    }});

    session.web.list.CalButton = session.web.list.Column.extend({
        format: function (row_data, options) {
            options = options || {};
            var attrs = {};
            if (options.process_modifiers !== false) {
                attrs = this.modifiers_for(row_data);
            }
            if (attrs.invisible) { return ''; }
            var template = 'ListView.row.calendar.button';
            return QWeb.render(template, {
                widget: this,
                prefix: session.session.prefix,
                disabled: attrs.readonly
            });
        }
    });

    session.web.list.columns.add('calbutton', 'session.web.list.CalButton');

    session.web_calendar.CalendarView.include({
        init: function (parent, dataset, view_id, options) {
            this._super(parent, dataset, view_id, options);
            this.color_code_map = {};
            this.last_domain = {};
        },
        event_data_transform: function(evt) {
            var res = this._super(evt);
            var self = this;
            if (this.read_color) {
                var color_key = evt[this.color_field];
                if (typeof color_key === "object") {
                    color_key = color_key[0];
                }
                
                this.read_resource_color(color_key).done(function(color){
                    if (color) {
                        res.color = color;
                        var event_objs = self.$calendar.fullCalendar('clientEvents', res.id);
                        if (event_objs.length == 1) { // Already existing obj to update
                            var event_obj = event_objs[0];
                            // update event_obj
                            event_obj.color = color;
                            self.$calendar.fullCalendar('updateEvent', event_obj);
                        }
                    }
                });
            }
            return res;
        },
        do_search: function(domain, context, _group_by) {
            this.last_domain = domain;
            this._super(domain, context, _group_by);
            this.set_free_slot_source(this.$calendar.fullCalendar('getView'), domain);
        },
        set_free_slot_source: function(view, domain) {
            var self = this;
            view.calendar.removeEvents(function(ev){return ev.className.indexOf('free_slot') >= 0});
            if (view.name == 'month'){
                return;
            }
            var event_source = function(start, end, callback) {
                var model = new session.web.Model("sale.order.line");
                model.call('read_resources', [domain || []])
                    .then(function (resources) {
                        view.calendar.removeEvents(function(ev){return ev.className.indexOf('free_slot') >= 0});
                        var slot_duration = view.calendar.option('slotMinutes')*1000*60;
                        var events = [];
                        var d_start = new Date();
                        var d_end = new Date();
                        var client_events = self.$calendar.fullCalendar('clientEvents', function(ev){
                            if (ev.start >= view.start && ev.start < view.end) {
                                return true;
                            }
                            if (ev.end <= view.end && ev.end > view.start) {
                                return true;
                            }
                        });

                        for(var d=Math.max(view.start.getTime(), d_start.getTime()); d<view.end.getTime(); d+=slot_duration) {
                            d_start.setTime(d);
                            d_end.setTime(d+slot_duration);
                            for(var i=0; i<resources.length; i++) {
                                var to_add = true;
                                for(var e=0; e<client_events.length; e++) {
                                    var ev = client_events[e];
                                    if (ev.title == resources[i].label) {
                                        if (ev.start >= d_start && ev.start < d_end) {
                                            to_add = false;
                                            break;
                                        } else if (ev.end <= d_end && ev.end > d_start) {
                                            to_add = false;
                                            break;
                                        } else if (ev.start < d_start && ev.end > d_end) {
                                            to_add = false;
                                            break;
                                        }
                                    }
                                }
                                if (to_add) {
                                    events.push({
                                        'start': d_start.toString('yyyy-MM-dd HH:mm:ss'),
                                        'end': d_end.toString('yyyy-MM-dd HH:mm:ss'),
                                        'title': resources[i].label,
                                        'color': resources[i].color,
                                        'className': 'free_slot resource_'+resources[i].value,
                                        'editable': false
                                    });
                                }
                            }
                        }
                        callback(events);
                    });
            }
            view.calendar.addEventSource({events: event_source, allDayDefault:false});
        },
        free_slot_click_data: function(event) {
            var self = this;
            var patt = /resource_(\d+)/;
            var data_template = self.get_event_data({
                start: event.start,
                end: event.end,
                allDay: false,
            });
            _.each(event.className, function(n){
                var r = patt.exec(n);
                if (r) {
                    data_template[self.color_field] = parseInt(r[1]);
                }
            });
            return data_template;
        },
        get_fc_init_options: function() {
            var res = this._super();
            var self = this;
            if (self.free_slots) {
                res.viewRender = function(view, element) {
                    self.view_render(self, view, element);
                    self.set_free_slot_source(view, self.last_domain);
                };
                res.eventClick = function (event) {
                    if (event.className.indexOf('free_slot') >= 0) {
                        self.open_quick_create(self.free_slot_click_data(event));
                    } else {
                        self.open_event(event._id,event.title);
                    }
                },
                res.timeFormat = {
                    'agenda': '',
                    '': ''
                };
                res.slotMinutes = 60;
            }
            res.slotEventOverlap = false;
            return res;
        },
        read_resource_color: function(key) {
            var self = this;
            var def = $.Deferred();
            if (this.color_code_map[key]) {
                def.resolve(this.color_code_map[key]);
            }
            else {            
                new session.web.Model(this.model).call('read_color', [key]).then(function(result) {
                    if (result) {
                        self.color_code_map[key] = result;
                    }
                    def.resolve(result);
                });
            }
            return def;
        },
        
        view_loading: function (fv) {
            var res =  this._super(fv);
            var attrs = fv.arch.attrs;
            this.read_color = false;
            this.free_slots;
            if (attrs.read_color) {
                this.read_color = attrs.read_color;
            }
            if (attrs.free_slots) {
                this.free_slots = attrs.free_slots;
            }
            return res
        },
        remove_event: function(id) {
            var id = parseInt(id);
            return this._super(id);
        }
    });

    session.web_calendar.SidebarFilter.include({
        set_filters: function() {
            this._super();
            if (this.view.read_color) {
                var self = this;
                _.forEach(self.view.all_filters, function(o) {
                    if (_.contains(self.view.now_filter_ids, o.value)) {
                        self.view.read_resource_color(o.value).done(function (color) {
                            self.$('div.oe_calendar_responsible span.underline_color_' + o.color).css('border-color', color);
                        });
                    }
                });
            }
        },
    });
}