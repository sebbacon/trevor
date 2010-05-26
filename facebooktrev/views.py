from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout

#uncomment the following two lines and the one below
#if you dont want to use a decorator instead of the middleware
#from django.utils.decorators import decorator_from_middleware
#from facebook.djangofb import FacebookMiddleware



import facebook.djangofb as facebook

from whatever.models import CustomUser
from whatever.models import Prediction
from utils import render
from utils import getThisYear
from models import FacebookUser
import settings

APP_URL = settings.FACEBOOK_APP_URL


@render('canvas.fbml')
@facebook.require_login()
def canvas(request):
    fb = request.facebook
    uid = fb.uid
    button = ('<fb:req-choice url="%s" label="Authorize My '
              'Application" />') % APP_URL
    is_app_user = fb.users.isAppUser(uid)
    has_authorised = False
    if is_app_user:
        check = fb.users.hasAppPermission
        has_authorized = check(ext_perm="publish_stream")\
                         and check(ext_perm="email")

    try:
        user = FacebookUser.objects.get(uid=uid)
    except FacebookUser.DoesNotExist:
        user = None
    if request.POST.get('link', ''):
        if has_authorized:
            user, created = FacebookUser.objects.get_or_create(uid=uid)
            email = fb.users.getInfo([uid],
                                     ['contact_email'])[0]['contact_email']
            try:
                trev_user = CustomUser.objects.get(email=email)
                user.user = trev_user
                user.save()
                return HttpResponseRedirect(reverse('canvas'))
            except CustomUser.DoesNotExist:
                pass

    elif (user and not user.user) and request.POST.get('link-manual', ''):
        if has_authorized:
            user, created = FacebookUser.objects.get_or_create(uid=uid)
            username = request.POST['email']
            password = request.POST['password']
            auth_user = authenticate(username=username, password=password)
            if auth_user:
                login(request, auth_user)            
                try:
                    trev_user = CustomUser.objects.get(email=auth_user.email)
                    user.user = trev_user
                    user.save()
                    return HttpResponseRedirect(reverse('canvas'))
                except CustomUser.DoesNotExist:
                    pass

    show_condensed_table = True
    current_page = request.GET.get('current_page', 1)
    full_table_url = "%s?%s" % (APP_URL, "full=1")
    predictions = Prediction.objects.filter(year=getThisYear())
    predictions = predictions.order_by('-score', '-goaldiff', 'created_date')
    predictions = predictions.all()
    can_show_full_table = True
    is_canvas = True
    app_url = APP_URL
    if request.GET.get('full', ''):
        show_full_table = True
        show_condensed_table = False
    return locals()

@render('tab.fbml')
@facebook.require_login()
def facebooktab(request):
    uid = request.POST['fb_sig_profile_user']
    user = FacebookUser.objects.get(uid=uid)
    show_condensed_table = True
    current_page = request.GET.get('current_page', 1)
    full_table_url = "%s?%s" % (APP_URL, "full=1")
    predictions = Prediction.objects.filter(year=getThisYear())
    predictions = predictions.order_by('-score', '-goaldiff', 'created_date')
    predictions = predictions.all()
    can_show_full_table = False
    app_url = APP_URL
    return locals()
    

@facebook.require_login()
def post_add(request):
    request.facebook.profile.setFBML(uid=request.facebook.uid, profile='Congratulations on adding PyFaceBook. Please click on the PyFaceBook link on the left side to change this text.')

    return request.facebook.redirect(APP_URL)

@facebook.require_login()
def ajax(request):
    return HttpResponse('hello world')


@render('changes.txt')
def notify_position_changes(request):
    predictions = Prediction.objects.filter(year=getThisYear(),
                                            user__facebookuser__isnull=False)
    fb = request.facebook
    news_added = []
    streams_updated = []
    for prediction in predictions:
        change = prediction.change_on_last_position
        if change == 0:
            continue
        message = "just moved %s %d places in WhatEverTrevor's league!"
        direction = change > 0 and "up" or "down"
        amount = abs(change)
        uid = prediction.user.facebookuser_set.get().uid
        message = message % (direction, amount)
        attachment = {'name':"WhatEverTrevor's league",
                      'href':APP_URL,
                      'caption':'{*actor*} ' + message,
                      'description':('WhatEverTrevor is a free game '
                      'about football, with a &pound;1million jackpot prize')}
        news = [{'message':"@:%s %s" % (uid, message)}]
        news_added.append(fb.dashboard.addNews(news,
                                               uid=uid))
        streams_updated.append(fb.stream.publish(attachment=attachment,
                                                 uid=uid))
    return locals()

