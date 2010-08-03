from sets import Set
import datetime
import simplejson
from itertools import chain
import cgi
import hashlib
import urllib

import simplejson as json

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect as redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db import transaction
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.flatpages.models import FlatPage

from models import RegistrationProfile, Prediction, CustomUser
from models import LeagueJoinStates
from models import League
from models import Competition
from models import Team
from models import RunningScore
from models import EmailMessage
from models import STATE_ACCEPTED, STATE_INVITED, STATE_APPLIED
from models import STATE_REJECTED, STATE_DECLINED
from forms import PredictionForm, UserForm, LeagueForm, NewLeagueForm
from forms import PredictionPasswordForm
from forms import NewPasswordForm
from forms import _setup_initial_prediction
from facebooktrev.models import FacebookUser
from utils import addToQueryString, getCurrentPrediction
from utils import getCurrentTable
from utils import getPreviousTable
from utils import render
import settings

ROWS_PER_PAGE = 25
def render_with_context(request,
                        template,
                        context,
                        **kw):
    pages = FlatPage.objects.all()
    kw['context_instance'] = RequestContext(request)
    context['pages'] = pages
    return render_to_response(template,
                              context,
                              **kw)


@render('login_form.html')
def login_form(request):
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        auth_user = authenticate(username=username, password=password)
        if auth_user:
            login(request, auth_user)
            url = request.GET.get('next', reverse('home'))
            return redirect(url)
        else:
            error = "Sorry, those details were not correct."
    return locals()

@render('subscribed.html')
def campaign_monitor_subscribed(request):
    return {}

def home(request):
    context = {}
    if request.user.is_anonymous():
        now = datetime.datetime.now()
        blog_date = blog_title = blog_content = None
        competition = Competition.objects\
                      .filter(start_date__lt=now,
                              close_date__gt=now)\
                      .order_by('start_date')
        if competition:
            competition = competition[0]
            predictions = Prediction.objects\
                          .filter(competition=competition)\
                          .all()[:10]
        else:
            competition = None 
            predictions = None
        context['blog_date'] = blog_date
        context['blog_title'] = blog_title
        context['blog_content'] = blog_content
        context['competition'] = competition
        context['predictions'] = predictions
        if request.method == "POST":
            # login attempt
            if request.POST.get('login', ''):
                username = request.POST['email']
                password = request.POST['password']
                user = authenticate(username=username,
                                    password=password)
                if user and not user.is_anonymous():
                    login(request, user)
                    return redirect(reverse('home'))
                else:
                    error = "Sorry, your details weren't recognised"
                    context = {'error': error}                    
                    return redirect(addToQueryString(reverse('home'),
                                                     context))
            else:
                # signup attempt
                form = PredictionForm(request.POST, request.FILES)
                if form.is_valid():
                    prediction = form.save()
                    request.session['prediction'] = prediction
                    request.session['competition'] = competition
                    return redirect(reverse('signup'))
                else:
                    context['form'] = form
        else:
            # default homepage
            context['form'] = PredictionForm()
        return render_with_context(request,
                                   'home.html',
                                   context)
    else:
        return redirect(reverse('logged_in'))

@render('make_prediction.html')
@login_required
@transaction.commit_manually
def make_prediction(request, competition=None):
    if not competition:
        competition = Competition.objects\
                      .get(pk=settings.CURRENT_COMPETITION_ID)
    competition = Competition.objects.get(pk=competition)
    has_password = request.user.has_usable_password()
    current_prediction = Prediction.objects\
                         .filter(competition=competition,
                                 user=request.user)\
                         .order_by('-created_date')
    current_prediction = current_prediction.count()\
                         and current_prediction[0] or None
    now = datetime.datetime.now()
    top_predictions = Prediction.objects\
                      .filter(competition=competition)
    if current_prediction:
        top_predictions = top_predictions\
                          .exclude(pk=current_prediction.pk)
    top_predictions = top_predictions[:3]
    if not competition.is_open():
        error = "This competition is now closed"
    if request.method == "POST":
        if has_password:
            form = PredictionForm(request.POST,
                                  request.FILES,
                                  default_table=current_prediction)
        else: 
            form = PredictionPasswordForm(request.POST,
                                          request.FILES,
                                          default_table=current_prediction)           
        if form.is_valid():
            this_year = datetime.datetime(settings.CURRENT_SEASON, 1, 1)
            prediction = form.save()
            saving = request.POST.get('save', '')
            prediction_obj = Prediction.objects.get_or_create(
                user=request.user,
                name=request.user.email,
                competition=competition   
                )[0]
            prediction_obj.teams.clear()
            for t_id in prediction:
                prediction_obj.teams.add(Team.objects.get(pk=t_id))
            prediction_obj.edited_date = now
            prediction_obj.save()
            score = prediction_obj.calculateScore(force=True)
            goaldiff = prediction_obj.calculateGoalDiff(force=True)
            position = prediction_obj.calculatePosition()
            prediction_obj.position = position
            
            if not has_password:
                request.user.set_password(form.cleaned_data['password1'])
                request.user.save()
            if saving:
                transaction.commit()                
                return redirect(reverse('logged_in') + '#comp-%s' % competition.pk)
            else:
                transaction.rollback()
                
    else:
        if has_password:
            form = PredictionForm(default_table=current_prediction)
        else:
            form = PredictionPasswordForm(default_table=current_prediction)
    return locals()

def _prediction_sorter(x, y):
    if x.my_prediction and not y.my_prediction:
        return 1
    elif y.my_prediction and not x.my_prediction:
        return -1
    elif not x.my_prediction and not y.my_prediction:
        return cmp(x.close_date, y.close_date)
    else:
        return cmp(x.my_prediction.created_date,
                   y.my_prediction.created_date)
    

def _decorate_with_predictions(competitions, user):
    decorated = []
    for competition in competitions:
        if competition.pk == settings.CURRENT_META_COMPETITION_ID:
            whichmodel = RunningScore
        else:
            whichmodel = Prediction
        try:
            my_prediction = whichmodel.objects.get(
                competition=competition,
                user=user)
        except whichmodel.DoesNotExist:
            my_prediction = None
        competition.my_prediction = my_prediction        
        decorated.append(competition)
    decorated.sort(lambda x, y: _prediction_sorter(y, x))
    return decorated                    

def _parse_facebook_friends(request):
    fb_sig = _get_facebook_cookie(request.COOKIES)
    uid = fb_sig.get('uid', None)
    session = request.session
    fbuser = request.user.facebookuser.get()
    if uid and uid != "None":        
        friends = json.load(urllib.urlopen(
            'https://graph.facebook.com/me/friends?access_token=%s'\
            % fb_sig['access_token']))['data']
        for friend in friends:
            try:
                fbfriend = FacebookUser.objects.get(uid=friend['id'])
                fbuser.friends.add(fbfriend)
            except FacebookUser.DoesNotExist:
                continue
    fbuser.save()

          
@render('logged_in.html')
def logged_in(request):
    if request.user.is_superuser:
        logout(request)
        return redirect(reverse('home'))
    fb = _get_facebook_cookie(request.COOKIES)
    if request.user.is_authenticated()\
           and request.user.has_prediction():
        current = getCurrentTable()
        leagues = request.user.leagues_by_state(STATE_ACCEPTED)
        my_leagues = leagues.filter(owner=request.user)
        now = datetime.datetime.now()
        open_or_entered = Q(start_date__lt=now,
                            close_date__gt=now) | \
                          Q(start_date__lt=now,
                            competition_date__gt=now,
                            prediction__user=request.user)
        open_comps = Competition.objects\
                     .filter(start_date__lt=now,
                             competition_date__gt=now)\
                     .distinct()\
                     .order_by('competition_date')
        open_comps = _decorate_with_predictions(open_comps,
                                                request.user)
        closed_comps = Competition.objects\
                       .filter(competition_date__lt=now)\
                       .exclude(pk=settings.FIRST_COMPETITION_ID)\
                       .all()
        closed_comps = _decorate_with_predictions(closed_comps,
                                                  request.user)
        future_comps = Competition.objects\
                       .filter(competition_date__gt=now,
                               start_date__gt=now).all()
        open_and_closed_comps = list(chain(open_comps, closed_comps))
        return locals()
    else:
        return redirect(reverse('home'))

@render('closed_competitions.html')
def closed_competitions(request):
    if request.user.is_authenticated()\
           and request.user.has_prediction():
        current = getCurrentTable()
        leagues = request.user.leagues_by_state(STATE_ACCEPTED)
        my_leagues = leagues.filter(owner=request.user)
        now = datetime.datetime.now()
        closed_comps = Competition.objects\
                       .filter(competition_date__lt=now)\
                       .exclude(pk=settings.FIRST_COMPETITION_ID)\
                       .all()
        closed_comps = _decorate_with_predictions(closed_comps,
                                                  request.user)
        return locals()
    else:
        return redirect(reverse('make_prediction'))

@render('competition.html')
def competition(request, competition=None):
    competition = Competition.objects.get(pk=competition)
    current = getCurrentTable()
    last = getPreviousTable(competition=competition)
    try:
        prediction = Prediction.objects\
                     .filter(competition=competition,
                             user=request.user).get()
        predictions = prediction.in_context()
        entered = True
    except Prediction.DoesNotExist:
        prediction = Prediction.objects\
                     .filter(competition=competition)
        if prediction.count():
            prediction = prediction[0]
            predictions = prediction.in_context()
        entered = False
    final = prediction.last_used_table
    max_goal_diff = current.max_goal_diff(last)
    #leagues = request.user.leagues_by_state(STATE_ACCEPTED)
    #if leagues.count():
    #    leagues_padding = list("x" * (3 - leagues.count() % 3))
    #else:
    #    leagues_padding = []
    #my_leagues = leagues.filter(owner=request.user)
    #applied_to_join = request.user.leagues_by_state(STATE_APPLIED)
    #need_approval = LeagueJoinStates.objects.filter(
    #    state=STATE_APPLIED,
    #    league__in=my_leagues)
    return locals()


@render('add_or_edit_league.html')
def add_or_edit_league(request, league=None):
    existing = ""
    if league:
        league = League.objects.get(pk=league)        
    if request.method == "POST":
        if league:
            form = LeagueForm(request.POST)
        else: 
            form = NewLeagueForm(request.POST)           
        if form.is_valid():
            if form.cleaned_data['join_leagues']:
                for league in form.cleaned_data['join_leagues']:
                    # apply to join these leagues
                    application = LeagueJoinStates.joined\
                                  .apply_to_league(league,
                                                   request.user)  
                url = reverse('logged_in')
                return redirect(url)
            else:
                could_join = Set([])
                applied = Set([])
                invited = Set([])
                # first, build three lists (applied, invited,
                # could_join) of leagues that people we're inviting
                # are already in
                for row in form.members.cleaned_data:
                    if row:
                        try:
                            member = CustomUser.objects.get(email=row['email'])
                        except CustomUser.DoesNotExist:
                            continue

                        user = request.user
                        leagues = member.leagues_by_state(
                            STATE_ACCEPTED)
                        # don't include leagues we've already decided
                        # not to join (or have been rejected from)
                        leagues = leagues.exclude(
                            leaguejoinstates__state=STATE_REJECTED,
                            leaguejoinstates__state=STATE_DECLINED,
                            leaguejoinstates__user=user
                            )
                        if leagues:
                            applied.update(leagues.filter(
                                leaguejoinstates__state=STATE_APPLIED,
                                leaguejoinstates__user=user
                                ))
                            invited.update(leagues.filter(
                                leaguejoinstates__state=STATE_INVITED,
                                leaguejoinstates__user=user
                                ))
                            could_join.update(leagues.exclude(
                                leaguejoinstates__user=user))
                if not request.POST.get('yes_really', '')\
                       and (could_join or applied or invited):
                    # present the user with a choice to join other
                    # leagues instead of making a new one
                    #
                    # XXX this is horrendous but I don't know how to
                    # do it better
                    choices = [(x.id, x.name) for x in could_join]
                    form.fields['join_leagues'].choices = choices
                    return locals()
                else:
                    # create a new league and invite people to join it
                    if not league:
                        league = League(name=form.cleaned_data['name'],
                                        owner=request.user)
                        league.save()
                        # the current user will be a member, of course
                        application = LeagueJoinStates(league=league,
                                                       user=request.user,
                                                       state=STATE_ACCEPTED)
                        application.save()
                    for row in form.members.cleaned_data:
                        if not row:
                            continue
                        email = row['email']
                        try:
                            member = CustomUser.objects.get(email=email)
                        except CustomUser.DoesNotExist:
                            create_user = CustomUser.objects.create_user
                            member = create_user(username=email,
                                                 email=email)
                            member.save()
                        try:
                            profile =  RegistrationProfile.objects\
                                      .filter(user=member).get()
                        except RegistrationProfile.DoesNotExist:
                            profile = RegistrationProfile.objects\
                                      .create_profile(member, email=False)
                        invite = LeagueJoinStates.joined\
                                 .invite_user(league, member)
                    url = reverse('logged_in')
                    return redirect(url)

    else:
        if league:
            form = LeagueForm()
        else:
            form = NewLeagueForm()
    return locals()

@render('league_invite_error.html')
def accept_league_invite(request, league="", key=""):
    league = League.objects.get(slug=league)
    profile = RegistrationProfile.objects.get_user(key,
                                                   only_activated=False)
    if profile:
        newuser = False
        if not profile.activated:
            profile = RegistrationProfile.objects.activate_user(key)
            newuser = True
        try:
            logout(request)
            user = profile.user
            joinstate = LeagueJoinStates.objects.filter(league=league,
                                                        user=user,
                                                        state=STATE_INVITED)\
                                                        .get()
            joinstate.accept(originator=user)
            if newuser:
                user = authenticate(username=user.email)
                login(request, user)
                return redirect(reverse('logged_in'))
            else:
                return redirect(reverse('login_form'))
        except LeagueJoinStates.DoesNotExist:
            if LeagueJoinStates.objects\
               .filter(league=league,
                       user=user,
                       state=STATE_ACCEPTED)\
               .count():
                # they've followed a link that they've previously
                # followed.  We log them in, in case they've not
                # actually made a prediction yet.
                user = authenticate(username=user.email)
                login(request, user)                                    
                return redirect(reverse('logged_in'))
                                   
            error = "No invite for user %s to league %s" % (user.email,
                                                            league.name)
    else:
        error = "No profile for key %s" % (key)
    return locals()

@render('league_invite_error.html')
def decline_league_invite(request, league="", key=""):
    league = League.objects.get(slug=league)
    profile = RegistrationProfile.objects.get_user(key,
                                                   only_activated=False)
    if profile:
        newuser = False
        if not profile.activated:
            profile = RegistrationProfile.objects.activate_user(key)
            newuser = True
        try:
            logout(request)
            user = profile.user
            joinstate = LeagueJoinStates.objects.filter(league=league,
                                                        user=user,
                                                        state=STATE_INVITED)\
                                                        .get()
            joinstate.decline(originator=user)
            if newuser:
                return redirect(reverse('home'))
            else:
                return redirect(reverse('login_form'))
        except LeagueJoinStates.DoesNotExist:
            error = "No invite for user %s to league %s" % (user.email,
                                                            league.name)
    else:
        error = "No profile for key %s" % (key)
    return locals()

@render('league_invite_error.html')
@login_required
def approve_league_application(request, league="", email=""):
    league = League.objects.get(slug=league)
    user = CustomUser.objects.get(email=email)
    owner = request.user
    if league.owner == owner:
        try:
            joinstate = LeagueJoinStates.objects.filter(league=league,
                                                        user=user,
                                                        state=STATE_APPLIED)\
                                                        .get()
            joinstate.approve(originator=request.user)
            return redirect(reverse('logged_in'))
        except LeagueJoinStates.DoesNotExist:
            error = "No application from user %s to league %s" % (email,
                                                                 league.name)
    else:
        error = "%s isn't owner of %s" % (owner, league)
    return locals()

@render('league_invite_error.html')
@login_required
def reject_league_application(request, league="", email=""):
    league = League.objects.get(slug=league)
    user = CustomUser.objects.get(email=email)
    owner = request.user
    if league.owner == owner:
        try:
            joinstate = LeagueJoinStates.objects.filter(league=league,
                                                        user=user).get() 
            joinstate.reject(originator=request.user)
            return redirect(reverse('logged_in'))
        except LeagueJoinStates.DoesNotExist:
            error = "No application frm user %s to league %s" % (email,
                                                                 league.name)
        except LeagueJoinStates.InvalidStateTransition:
            error = "No can't reject user %s from league %s" % (email,
                                                                league.name)
            
    else:
        error = "%s isn't owner of %s" % (owner, league)
    return locals()

@render('league_apply.html')
def league_apply(request):
    return locals()

@render('league_create.html')
def league_create(request):
    return locals()

@render('facebookinvite.html')
def facebookinvite(request):
    return locals()


def _get_facebook_cookie(cookies):
    api_key = settings.FACEBOOK_API_KEY
    if api_key not in cookies:
        return {}

    prefix = "fbs_%s" % api_key 
    try:
        tmp = cgi.parse_qs(cookies[prefix])
    except KeyError:
        return {}
    params = {}
    for k, v in tmp.items():
        params[k] = v[0]
    payload = ''
    for k in sorted(params):
        if k != "sig":
            value = params[k]
            payload += "%s=%s" % (k, value)

    hasher = hashlib.md5(payload)

    hasher.update(settings.FACEBOOK_SECRET_KEY)
    digest = hasher.hexdigest()
    if digest == params["sig"]:
        params['is_session_from_cookie'] = True
        return params
    else:
        return {}

def login_via_facebook(request):
    signup_via_facebook(request, new_prediction=False)
    return redirect(reverse('home'))

def signup_via_facebook(request,
                        new_prediction=True):
    fb_sig = _get_facebook_cookie(request.COOKIES)
    uid = fb_sig.get('uid', None)
    session = request.session
    if uid and uid != "None":        
        profile = json.load(urllib.urlopen(
            'https://graph.facebook.com/me?access_token=%s'\
            % fb_sig['access_token']))
        try:
            user = CustomUser.objects.get(email=profile['email'])
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(
                username=profile['email'],
                email=profile['email'],
                can_email=True,
                first_name=profile['first_name'],
                last_name=profile['last_name'],
                is_active=True)
        try:
            fbuser = FacebookUser.objects.get(user=user)
        except FacebookUser.DoesNotExist:
            fbuser = FacebookUser.objects.create(uid=uid,
                                                 user=user)
        if new_prediction:
            _setup_initial_prediction(user,
                                      session['prediction'],
                                      session['competition'])
        notify_signedup(request, uid)
        user = authenticate(username=user.email)
        login(request, user)
        facebook_friends = _parse_facebook_friends(request)

    return redirect(reverse('home'))
    

def notify_signedup(request, uid):
    fb = request.facebook
    message = "just joined WhatEverTrevor"
    attachment = {'name':"WhatEverTrevor's premier league",
                  'href':"http://www.whatevertrevor.co.uk/",
                  'caption':'{*actor*} ' + message,
                  'description':('WhatEverTrevor is a free game '
                                 'about football, with a jackpot prize')}
    news = [{'message':"@:%s %s" % (uid, message)}]
    fb.dashboard.addNews(news,
                         uid=uid)
    fb.stream.publish(attachment=attachment,
                      uid=uid)


def signup(request):
    context = {}
    session = request.session
    if request.method == "POST":
        # signup attempt
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(prediction=session['prediction'],
                                competition=session['competition'])
            user = authenticate(username=profile.user.email)
            login(request, user)
            return redirect(reverse('home'))
        else:
            context['form'] = form
    else:
        # default homepage
        context['form'] = UserForm()
    return render_with_context(request,
                               'signup.html',
                               context)

def json_get_history(request, email=""):
    if not request.user.is_anonymous():
        if email:
            user = CustomUser.objects.get(email=email)
        else:
            user = request.user
        prediction = getCurrentPrediction(user)
        history = prediction.positions\
                  .order_by('date')\
                  .all()
        data = {'count': history.count(),
                'positions': [x.position for x in history],
                'email':user.email}
    else:
        data = {'count':0,
                'positions':[],
                'email':''}
    return HttpResponse(simplejson.dumps(data),
                        mimetype='application/json')        

def table(request, current_page=1, competition=None):
    if not competition:
        competition = Competition.objects\
                      .get(pk=settings.CURRENT_COMPETITION_ID)
    competition = Competition.objects.get(pk=competition)
    context = {}
    predictions = competition.predictions_with_rank()
    context['predictions'] = predictions
    context['current_page'] = current_page    
    context['competition'] = competition
    return render_with_context(request,
                               'table.html',
                               context)

# user functions
def do_login(request, key):
    profile = RegistrationProfile.objects.get_user(key)
    if profile:
        user = authenticate(username=profile.user.email)
        login(request, user)
    return redirect("/")

def activate_user(request, key):
    profile = RegistrationProfile.objects.activate_user(key)
    error = notice = ""
    if not profile:
        error = "Sorry, that key was invalid"
    else:
        notice = "Thanks, you've successfully confirmed your email"
        user = authenticate(username=profile.user.email)
        login(request, user)
    context = {'error': error,
               'notice': notice}
    return redirect(addToQueryString(reverse('home'),
                                                 context))
@render('reset_password_request.html')
def reset_password_request(request):
    if request.method == "POST":
        email = request.POST['email']        
        user = None
        messages = []
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.append("I couldn't find a user with email address %s" % email)
        else:
            try:
                profile = user.registrationprofile_set.get()
                profile.send_reset_password_email()
                messages.append(("Password change email sent. Please "
                                 "check your %s inbox. If it isn't "
                                 "there,  check your spam folders")\
                                % email)
            except RegistrationProfile.DoesNotExist:
                messages.append("I couldn't find a profile for %s" % email)
                
    return locals()

@render('reset_password.html')
def reset_password(request, key):
    profile = RegistrationProfile.objects\
              .get_user(key,
                        only_activated=False)
    user = profile.user
    if request.method == "POST":
        form = NewPasswordForm(request.POST, request.FILES)
        if form.is_valid():
            user = authenticate(username=user.email)
            login(request, user)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect(reverse('home'))
    else:
        form = NewPasswordForm()
    return locals()
    
def email_reminder(request):
    messages = []
    if request.method == "POST":
        email = request.POST['email']
        
        user = None
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.append("I couldn't find a user with email address %s" % email)
        else:
            # we assume that if they previously unsubscribed, they've
            # now changed their minds
            user.unsubscribed = False
            user.save()
            profile = user.registrationprofile_set.get()
            profile.send_activation_email()
            messages.append("Activation email re-sent. Please check your %s inbox. If it isn't there, check your spam folders" % email)
    context = {'messages':messages}
    return render_with_context(request,
                               "email_reminder.html",
                               context) 

def process_email_queue(request):
    emails = EmailMessage.objects.filter(date_sent__isnull=True)
    for email in emails:
        print email.get_body()
    

def logout_view(request):
    logout(request)
    key = settings.FACEBOOK_API_KEY,
    prefixes = ["fbs_%s" % key,
                "%s_expires",
                "%s" % key,
                "%s_session_key" % key,
                "%s_user" % key]
    response = redirect(reverse('home'))        
    if request.COOKIES.has_key(prefixes[0]):
        for prefix in prefixes:
            response.delete_cookie(prefix)
    return response
