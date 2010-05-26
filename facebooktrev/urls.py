from django.conf.urls.defaults import *

import views

# You'd want to change this to wherever your app lives
urlpatterns = patterns('facebook.views',
    # This is the canvas callback, i.e. what will be seen
    # when you visit http://apps.facebook.com/<appname>.
    url(r'^canvas/$', views.canvas, name="canvas"),
    url(r'^canvas/tab/', views.facebooktab, name="facebooktab"),
    url(r'^notify/', views.notify_position_changes, name="notify"),
)
