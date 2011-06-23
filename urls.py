from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin

admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    (r'^api/', include('webapi.urls')),
    (r'^network/', include('networks.urls')),
    (r'^event/', include('events.urls')),
    (r'^report/', include('reportmeta.urls')),
    ('^$', 'django.views.generic.simple.direct_to_template', {'template': 'home.html'}),
    (r'^accounts/', include(admin.site.urls)),
    
    url(r'login/', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),

    url(r'^oauth/request_token/$','piston.authentication.oauth_request_token'),
    url(r'^oauth/authorize/$','piston.authentication.oauth_user_auth'),
    url(r'^oauth/access_token/$','piston.authentication.oauth_access_token'),
    
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)