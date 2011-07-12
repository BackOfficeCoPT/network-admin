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

try:
    import simplejson as json
except ImportError:
    import json

from django.db import models
from django.utils.translation import ugettext as _
from django.contrib import admin
from django.contrib.auth.models import User

from netadmin.networks.models import Host


ALERT_LEVELS = (
    (0, _('Low')),
    (1, _('Medium')),
    (2, _('High'))
)


class EventType(models.Model):
    """A very simple model written to make managing events types easier"""
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        from netadmin.reports.models import ReportMetaEventType
        
        # delete relations between event type and reports
        related = ReportMetaEventType.objects.filter(event_type=self)
        related.delete()
        
        super(EventType, self).delete(*args, **kwargs)
        
    def _events(self):
        return Event.objects.filter(event_type=self)
    events = property(_events)


class Event(models.Model):
    """
    Event model class represents single notification reported to the Network
    Administrator. The following fields are defined:
        * message - name and/or description of an event
        * timestamp - moment, when event occured on host
        * event_type - foreign key to the EventType object which simply stores
          short and readable event name like **INFO** or **WARNING**
        * source_host - foreign key to the Host object; this is the host from
          where the event came
        * monitoring_module - identifier of a monitoring module, which is
          a module that provides more specific data about the event
        * monitoring_module_fields - serialized fields for the monitoring
          module; data provided by monitoring module is based on these fields
        * checked - True means that event has been marked by user as known
          (actually this field is important only for alerts, where information
          about event status is really important)
    
    Note 1: Only last two fields are optional.
    Note 2: Although event hasn't *user* field specified, we can say that
            event belongs to the user who ownes the source host.
    """
    message = models.TextField()
    short_message = models.CharField(max_length=200)
    timestamp = models.DateTimeField()
    protocol = models.CharField(max_length=30)
    event_type = models.ForeignKey(EventType)
    source_host = models.ForeignKey(Host, blank=True)
    fields_class = models.CharField(max_length=50, null=True, blank=True)
    fields_data = models.TextField(null=True, blank=True)
    checked = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.message

    def get_details(self):
        """Returns event details extracted from monitoring module fields"""
        fields = json.loads(self.fields_data)
        return fields
    
    def _html_message(self):
        return self.message.replace('\n', '<br />')
    html_message = property(_html_message)
    
    def _user(self):
        return self.source_host.user
    user = property(_user)
    
    def get_html(self):
        """Notifier support: returns event data in HTML"""
        title = '%s %s' % (str(self.timestamp), self.event_type.name)
        return '<h2>%s</h2>%s' % (title, self.html_message)
    
    def is_alert(self, user):
        try:
            alert = Alert.objects.get(user=user, event_type=self.event_type)
        except Alert.DoesNotExist:
            return 0
        return alert.level
            
class Alert(models.Model):
    """
    Alerts are user-defined priorities assigned to events types.
    """
    event_type = models.ForeignKey(EventType)
    user = models.ForeignKey(User)
    level = models.IntegerField(choices=ALERT_LEVELS)

admin.site.register(Event)   
admin.site.register(EventType)