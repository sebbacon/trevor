from django.conf.urls.defaults import *
import views

urlpatterns = patterns('whatever',
    url(r'^$', views.home, name="home"),
    url(r'^login/$', views.home, name="login"),
    url(r'^home/$', views.logged_in, name="logged_in"),
    url(r'^facebookinvite/$', views.facebookinvite, name="facebookinvite"),
    url(r'^closed/$',
        views.closed_competitions,
        name="closed_competitions"),
    url(r'^table/(?P<competition>\d+)/$',
        views.table,
        name="table"),
    url(r'^table/(?P<competition>\d+)/(?P<current_page>\d+)/$',
        views.table,
        name="table"),

    # competitions
    url(r'^competition/(?P<competition>\d+)/$',
        views.competition,
        name="competition"),
    url(r'^competition/(?P<competition>\d+)/make_selection/$',
        views.make_prediction,
        name="make_prediction"),

    # emails
    url(r'^email/$',
        views.process_email_queue,
        name="process_email_queue"),
                       
    # users
    url(r'^json_get_history/$',
        views.json_get_history,
        name="json_get_history"),
    url(r'^json_get_history/(?P<email>.+)/$',
        views.json_get_history,
        name="json_get_history_for"),
    url(r'^login/(?P<key>\w+)/$',
        views.do_login,
        name="login"),
    url(r'^logout/$',
        views.logout_view,
        name="logout"),
    url(r'^signup/$',
        views.signup,
        name="signup"),
    url(r'^fb_signup/$',
        views.signup_via_facebook,
        name="signup_via_facebook"),
    url(r'^login_form/$',
        views.login_form,
        name="login_form"),
    url(r'^fb_login/$',
        views.login_via_facebook,
        name="login_via_facebook"),
    url(r'^subscribed/$',
        views.campaign_monitor_subscribed,
        name="subscribed"),
    url(r'^activate/(?P<key>\w+)/$',
        views.activate_user,
        name="activate"),
    url(r'^reset/$',
        views.reset_password_request,
        name="reset_password_request"),
    url(r'^reset/(?P<key>\w+)/$',
        views.reset_password,
        name="reset_password"),
    url(r'^trevorusers.csv$',
        views.user_csv,
        name="user_csv"),
                       
    # leagues
    url(r'^add_league/$',
        views.add_or_edit_league,
        name="add_league"),
    url(r'^edit_league/(?P<league>.+)/$',
        views.add_or_edit_league,
        name="edit_league"),
    url(r'^league_apply/$',
        views.league_apply,
        name="league_apply"),
    url(r'^league_create/$',
        views.league_create,
        name="league_create"),
    url(r'^accept/(?P<league>.+)/(?P<key>\w+)/$',
        views.accept_league_invite,
        name="accept_league_invite"),
    url(r'^decline/(?P<league>.+)/(?P<key>\w+)/$',
        views.decline_league_invite,
        name="decline_league_invite"),
    url(r'^approve/(?P<league>.+)/(?P<email>.+)/$',
        views.approve_league_application,
        name="approve_league_application"),
    url(r'^reject/(?P<league>.+)/(?P<email>.+)/$',
        views.reject_league_application,
        name="reject_league_application"),

    # statistics
    url(r'^statistics/$',
        views.statistics,
        name="statistics"),

)

