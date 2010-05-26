from django.conf.urls.defaults import *
import views

urlpatterns = patterns('holding',
    url(r'^$', views.home, name="holdinggame"),
    url(r'^waitinglist/$', views.home2, name="holdingsignup"),
)
