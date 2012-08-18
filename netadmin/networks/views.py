#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author: Amit Pal <amix.pal@gmail.com>
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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.create_update import update_object, delete_object
from django.views.generic.list_detail import object_detail
from django.views.generic.simple import direct_to_template, redirect_to
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse,HttpResponseRedirect
try:
    from search.core import search
except ImportError:
    search = None

from netadmin.events.models import Event, EventType
from netadmin.shortcuts import get_timezone, get_netmask, get_user_events, \
	get_hosts
from netadmin.permissions.utils import filter_user_objects, \
    get_object_or_forbidden, grant_access, grant_edit, revoke_access, \
    revoke_edit, user_has_access

import datetime
now = datetime.datetime.now()

from models import Host, Network, NetworkHost, HostCommand
from forms import HostCreateForm, HostUpdateForm, NetworkCreateForm, \
    NetworkUpdateForm, SubnetCreateFrom, RemoteCommandForm
from utils import get_subnet
from netadmin.events.utils import filter_user_events, range_check, \
	get_latlng
from netadmin.permissions.models import ObjectPermission

@login_required
def host_list(request, page=None):
    search_phrase = request.GET.get('s')
    if search_phrase and search != None:
        hosts = search(Host, search_phrase)
    else:
        hosts = Host.shared_objects(request.user)
        
    paginator = Paginator(list(hosts), 10)
    
    page = page or request.GET.get('page', 1)
    try:
        hosts = paginator.page(page)
    except PageNotAnInteger:
        hosts = paginator.page(1)
    except EmptyPage:
        hosts = paginator.page(paginator.num_pages)
    extra_context = {
        'hosts': hosts,
        'url': reverse('host_list')
    }
    return direct_to_template(request, 'networks/host_list.html',
                              extra_context=extra_context)

@login_required
def host_detail(request, object_id):
    
    host, edit = get_object_or_forbidden(Host, object_id, request.user)
    remote_command = HostCommand.objects.filter(host=object_id)
    
    extra_context = {
        'can_edit': edit,
        'remote_command': remote_command
    }
    
    return object_detail(request, Host.objects.all(), object_id,
                         extra_context=extra_context)

@login_required
def host_create(request):
    
    if request.method == 'POST':
        form = HostCreateForm(request.POST)
        if form.is_valid():
            my_inst = form.save(commit=False)
            zone_data = get_timezone(user=request.user.username)
            my_inst.timezone = zone_data
            my_inst.save()
            return redirect_to(request, url=my_inst.get_absolute_url())
    extra_context = {
        'form': HostCreateForm(initial={'user': request.user.pk})
    }
    return direct_to_template(request, 'networks/host_form.html', 
						      extra_context)

@login_required
def host_update(request, object_id):
    
    host, edit = get_object_or_forbidden(Host, object_id, request.user)    
    if not edit:
        raise Http404()
    
    return update_object(request, object_id=object_id,
                         form_class=HostUpdateForm,
                         template_name='networks/host_update.html')

@login_required
def host_delete(request, object_id):
    
    host, edit = get_object_or_forbidden(Host, object_id, request.user)
    
    if host.user != request.user:
        raise Http404()

    return delete_object(request, object_id=object_id, model=Host,
                         post_delete_redirect=reverse('host_list'))

@login_required
def network_list(request, page=None):
    search_phrase = request.GET.get('s')
    if search_phrase and search != None:
        nets = search(Network, search_phrase)
        # TODO
        # filter search results by user access
    else:
        nets = Network.shared_objects(request.user)
        
    paginator = Paginator(list(nets), 10)
    
    page = page or request.GET.get('page', 1)
    try:
        nets = paginator.page(page)
    except PageNotAnInteger:
        nets = paginator.page(1)
    except EmptyPage:
        nets = paginator.page(paginator.num_pages)
    
    extra_context = {
        'networks': nets,
        'url': '/network/network/list/'
    }
    return direct_to_template(request, 'networks/network_list.html',
                              extra_context=extra_context)

@login_required
def network_create(request):
    if request.method == 'POST':
        form = NetworkCreateForm(request.POST)
        if form.is_valid():
            network = form.save()
            return redirect_to(request, url=network.get_absolute_url())
    
    extra_context = {
        'form': NetworkCreateForm(initial={'user': request.user.pk})
    }
    return direct_to_template(request, 'networks/network_form.html',
                              extra_context)

@login_required
def network_update(request, object_id):
    network = Network.objects.get(pk=object_id)
    
    if not network.can_edit(request.user):
        raise Http404()
    
    return update_object(request, object_id=object_id,
                         form_class=NetworkUpdateForm,
                         template_name='networks/network_update.html')

@login_required
def network_delete(request, object_id):
    
    network = Network.objects.get(pk=object_id)
    
    if network.user != request.user:
        raise Http404()
    
    return delete_object(request, object_id=object_id, model=Network,
                         post_delete_redirect=reverse('network_list'))

@login_required
def network_events(request, object_id):
    """Display events related to a network
    """
    network = Network.objects.get(pk=object_id)

    if not network.has_access(request.user):
        return Http404()

    queryset = Network.shared_objects(request.user)
    related_hosts = [nh.host.pk for nh in NetworkHost.objects.filter(network=network)]
    events = Event.objects.filter(source_host__pk__in=related_hosts)
    extra_context = {
        'events': events,
        'can_edit': network.can_edit(request.user)
    }
    return object_detail(request, queryset, object_id,
                         extra_context=extra_context,
                         template_name='networks/network_events.html')

@login_required
def share(request, object_type, object_id):
    model = Network if object_type == 'network' else Host
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    user_id = request.POST.get('share')
    if user_id:
        user = User.objects.get(pk=user_id)
        grant_access(obj, user)
    return share_list(request, object_type, object_id)

@login_required
def share_not(request, object_type, object_id, user_id):
    model = Network if object_type == 'network' else Host
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    user = User.objects.get(pk=user_id)
    revoke_access(obj, user)
    return share_list(request, object_type, object_id)

@login_required
def share_edit(request, object_type, object_id, user_id):
    model = Network if object_type == 'network' else Host
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    user = User.objects.get(pk=user_id)
    
    permission_obj = ObjectPermission.objects.filter(object_id=object_id)
    for perm in permission_obj:
		edit_status = perm.edit
		
    if edit_status:
		revoke_edit(obj, user)
    else:
        grant_edit(obj, user)
    return share_list(request, object_type, object_id)

@login_required
def share_list(request, object_type, object_id):
    model = Network if object_type == 'network' else Host
    obj, edit = get_object_or_forbidden(model, object_id, request.user)
    all_users = User.objects.exclude(pk=request.user.pk)
    other_users = []
    share_object = []
    
    for user in all_users:
        if not user_has_access(obj, user):
            other_users.append(user)
    
    permission_obj = ObjectPermission.objects.filter(object_id=object_id)
    
    for perm in permission_obj:
		share_object.append({'user': perm.user, 'edit': perm.edit,
							'id':perm.user.id })
		
    extra_context = {
	'object': obj,
	'object_type': object_type,
	'other_users': other_users,
	'objects_detail': share_object
	}
    return direct_to_template(request, 'networks/share.html', 
							  extra_context)

@login_required
def subnet_network(request):
    if request.method == 'POST':
        form = SubnetCreateFrom(request.POST)
        if form.is_valid():
            subnet = form.cleaned_data['Subnet_Address']
            ip = form.cleaned_data['IP_Address']
            user_host = get_hosts(user=request.user)
            hosts_list = get_subnet(user_host, subnet,ip)
            subnet_network = form.save()
            network_obj = Network.objects.get(name__exact = form.cleaned_data['name'])
    
            for hosts in hosts_list:
                network_entry = NetworkHost(network_id = network_obj.id, 
											host_id = hosts.id)
                network_entry.save()
    
            extra_context = {
                'form': SubnetCreateFrom(initial={'user': request.user.pk}),
                'host_list': hosts_list
                }
    
            return redirect_to(request, url=subnet_network.get_absolute_url())
    else:
        form = SubnetCreateFrom()
    
    extra_context = {
        'form':SubnetCreateFrom(initial={'user': request.user.pk})
    }
    return direct_to_template(request,'networks/subnet_form.html',
							  extra_context)

@login_required
def network_detail(request, object_id):
    network_obj = Network.objects.get(id = object_id)
    host_list = []
    
    if network_obj.subnet:
        hosts = NetworkHost.objects.filter(network = object_id)
        host_id = hosts.values('host')
        for h_id in host_id:
            for key,value in h_id.items():
                host_obj = Host.objects.get(pk= value)
                host_list.append(host_obj)
    else:
        host_list = Host.objects.filter(user=request.user)
    
    extra_context = {
        'hosts': host_list,
        'id':object_id
    }
    return direct_to_template(request,'networks/network_detail.html',
							  extra_context)

@login_required
def network_select(request,object_id):
    if request.method == 'POST':
        host = request.POST.getlist('host')
        NetworkHost.objects.filter(network = object_id).delete()
        for hosts in host:
            network_entry = NetworkHost(network_id = object_id, 
										host_id = hosts.replace("/",""))
            network_entry.save()
    
    return HttpResponseRedirect(reverse('network_list'))

def trace_route(request, object_id):
	if object_id == str(request.user.id):
		geoIP, event_type, event_time, event_mesg, hosts = ([] for i in range(5))
		for host in get_hosts(user=request.user):
			geo_range = range_check(host.ipv4)
			hosts.append(host.ipv4)
			geoIP.append( '%s' % (geo_range[0][0]))
		
		geo_latlng = get_latlng(geoIP)
		events = get_user_events(user=request.user)
		for obj in events:
			event_time.append(str(obj.timestamp))
			event_mesg.append(obj.message)
			event_types = EventType.objects.get(pk=obj.event_type_id)
			event_type.append(event_types.name)
			
		extra_context = {
			'latlng': geo_latlng,
			'message': event_mesg,
			'timestamp': event_time,
			'event_type':event_type,
			'host':hosts
		}
		return direct_to_template(request, 'networks/private_map.html',
							  extra_context)
							  
def remote_command(request, object_id):
	if request.method == 'POST':
		form = RemoteCommandForm(request.POST)
		if form.is_valid():
			form_inst = form.save(commit=False)
			form_inst.user = request.user
			form_inst.host = object_id
			form_inst.save();
			from netadmin.utils.command import exec_scheduler
			command_obj = HostCommand.objects.get(scheduling=1)
			exec_scheduler(request.user,command)
			return HttpResponseRedirect(reverse('host_list'))
	else:
		form = RemoteCommandForm()
	
	extra_context = {
		'form':RemoteCommandForm(initial={'user': request.user.pk})
    }	
	return direct_to_template(request, 'networks/network_remote.html',
							  extra_context=extra_context)

def delete_command(request, object_id):
	command_obj = HostCommand.objects.filter(pk=object_id).delete()
	
