#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Piotrek Wasilewski <wasilewski.piotrek@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *


urlpatterns = patterns('netadmin.plugins.views',
    url(r'^settings/$', 'plugins_settings', name='plugins_settings'),
    url(r'^widgets/settings/$', 'widgets_settings', name='widgets_settings'),
    url(r'^widgets/remove/(?P<widget_remove>\d+)/$', 'widgets_settings', name='widgets_remove'),
    url(r'^widget/(?P<widgetsettings_id>\d+)/$', 'widget_detail', name='widget_detail'),
    url(r'^widget/up/(?P<widget_up>\d+)/$', 'widgets_settings', name='widget_up'),
    url(r'^widget/down/(?P<widget_down>\d+)/$', 'widgets_settings', name='widget_down'),
    url(r'^widget/ajax/$', 'widgets_ajax', name='widget_ajax'),
)

urlpatterns += patterns('netadmin.plugins.ajax_view',
	url(r'^ajax/(?P<object_id>\d+)/$', 'ajax_render_data', name='ajax_render_data'),
)
