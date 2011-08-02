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

from django import template
from django.template.loader import get_template
from django.template import Context

from django.utils.translation import ugettext as _

from netadmin.plugins.models import Dashboard


register = template.Library()


@register.simple_tag
def render_widget(widget):
    template_name = widget.template_name
    context = widget().context()
    t =  get_template(template_name)
    return t.render(Context(context))

@register.inclusion_tag("plugins/dashboard.html")
def render_dashboard(user):
    dashboard, created = Dashboard.objects.get_or_create(user=user,
                                                         name=_("Dashboard"))
    
    widgets_settings = dashboard.widgetsettings_set.all().order_by("column")
    context = {
        "widgets_settings": widgets_settings
    }
    return context
