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

import datetime

from django.core.urlresolvers import reverse

from netadmin.events.models import Event, EventType
from netadmin.networks.models import Host
from netadmin.utils.testutils import EventBaseTest
from netadmin.users.models import UserProfile


class EventTest(EventBaseTest):
    """Tests for hosts
    """
    
    def setUp(self):
        super(EventTest, self).setUp()
        self.source_host = Host(name='Host', ipv4='1.2.3.4', user=self.user,timezone = 'Asia/Kolkata')
        self.source_host.save()
        
       
        
        event_type = EventType(name='INFO', user=self.user)
        event_type.save()
        
        event_data = {
            'message': 'Message',
            'short_message': 'short message',
            'event_type': event_type,
            'timestamp': '%s' % str(datetime.datetime.now()),
            'source_host': self.source_host
        }
        self.event = Event.objects.create(**event_data)
        
    def test_event_detail(self):
        """Get event's details
        """
        url = reverse('event_detail', kwargs={'object_id': self.event.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('object', response.context)
        self.assertIn('check_form', response.context)

    def test_event_list(self):
        """Get events list
        """
        response = self.client.get(reverse('events_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('events', response.context)
        
    def test_shared_event_detail(self):
        """
        Only a user that has access to a source host should be able to
        see event's details
        """
        other_user =  self.create_user('other', 'otherpassword')
        self.source_host.user = other_user
        self.source_host.save()
        url = reverse('event_detail', kwargs={'object_id': self.event.pk})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

        self.source_host.share(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        self.source_host.user = self.user
        self.source_host.save()
