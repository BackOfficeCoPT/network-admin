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

from netadmin.plugins.actions import run_action, actions_list

register = template.Library()

@register.filter(name='action')
def action_filter(action_object, action_name):
    return run_action(action_name, action_object, pass_result=True)

@register.simple_tag
def action_extend(action_name, tag_name, action_object=None):
    actions = actions_list(active=True)
    result_content = ''
    for name, callback in actions:
        if name == action_name:
            result_content += '<%s>%s</%s>' % \
                (tag_name, callback(action_object), tag_name)
    return result_content    
