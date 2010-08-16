from django.conf.urls.defaults import *
import views

urlpatterns = patterns('manager',
    url(r'^$',
        views.index,
        name="index"),
    url(r'^statistics/$',
        views.statistics,
        name="statistics"),
    url(r'^campaignmonitor/$',
        views.campaignmonitor,
        name="campaignmonitor"),
    url(r'^trevorusers.csv$',
        views.user_csv,
        name="user_csv"),
)

