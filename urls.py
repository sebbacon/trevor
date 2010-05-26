from django.conf.urls.defaults import *
from settings import MEDIA_ROOT
from django.views.static import serve
from django.views.generic.simple import direct_to_template

import trevor

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enablese admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', serve,
     {'document_root': MEDIA_ROOT,
      'show_indexes': True}),
    ('^', include('whatever.urls')),
    ('^facebook/', include('facebooktrev.urls')),
    (r'^privacy/$',
     direct_to_template,
     {'template': 'privacy.html'}),
    (r'^terms/$',
     direct_to_template,
     {'template': 'terms.html'}),
    (r'^xd_receiver.htm$',
     direct_to_template,
     {'template': 'xd_receiver.htm'}),
     
)
