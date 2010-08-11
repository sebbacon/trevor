# python
import datetime
import random
import re
import sha
import math

# django
from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User, UserManager
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.db.models import Model 

from signals import position_changed

from basemodel import AutoSlugModel

SHA1_RE = re.compile('^[a-f0-9]{40}$')
STATE_INVITED = 0
STATE_DECLINED = 1
STATE_ACCEPTED = 2
STATE_APPLIED = 3
STATE_REJECTED = 4

INVITE_STATES = {
    STATE_INVITED: 'Invited',
    STATE_DECLINED: 'Declined',    
    STATE_ACCEPTED:'Accepted',
    STATE_APPLIED: 'Applied',
    STATE_REJECTED: 'Rejected'    
}

class League(AutoSlugModel):
    name = models.CharField(max_length=80)
    slug = models.SlugField(max_length=80)
    date = models.DateField(auto_now_add=True)
    owner = models.ForeignKey("CustomUser")


    def members_and_applicants(self):
        return self.customuser_set.all()

    def members_invited(self):
        return self.customuser_set.\
               filter(leaguejoinstates__state=STATE_INVITED)\
               .all().order_by("-current_score")

    def members(self):
        return self.customuser_set.\
               filter(leaguejoinstates__state=STATE_ACCEPTED)\
               .all().order_by("-current_score")

    def __unicode__(self):
        return "%s" % self.name
    
    @permalink
    def get_absolute_url(self):
        return ("league", (self.slug,))


class CustomUser(User):
    leagues = models.ManyToManyField(League,
                                     blank=True,
                                     through="LeagueJoinStates")
    can_email = models.BooleanField(default=True)
    objects = UserManager()
    current_score = models.IntegerField(default=0)
    supported_team = models.ForeignKey('Team',
                                       blank=True,
                                       null=True)
    login_count = models.IntegerField(default=0)
    
    @property
    def display_name(self):
        if self.first_name:
            name = self.first_name
        else:
            name = self.email[:self.email.find("@")]
        return name
    
    def has_prediction(self):
        return Prediction.objects.filter(user=self)

    def leagues_by_state(self, state):
        return self.leagues.filter(leaguejoinstates__state=state)

    def completed_competitions(self):
        now = datetime.datetime.now()
        return Competition.objects.filter(
            competition_date__lt=now,
            prediction__user=self)

    def get_facebook_friends(self):
        return self.facebookuser.get().friends.all()
    
    def __unicode__(self):
        return self.email
    
    @permalink
    def get_absolute_url(self):
        return ("user", (self.id,))


class LeagueJoinStatesManager(models.Manager):
    """
        Managing the LeagueJoinStates objects
    """

    def invite_user(self, league, user):
        if LeagueJoinStates.objects.filter(league=league,
                                       user=user,
                                       state=STATE_INVITED):
            raise LeagueJoinStates.InvalidStateTransition()
        
        invite = LeagueJoinStates(league=league,
                                  user=user,
                                  state=STATE_INVITED)
        invite.save()
        
        current_site = Site.objects.get_current()
        subject = "Invitation to join %s" % league.name
        profile =  RegistrationProfile.objects.filter(user=user).get()

        email_context = {'league': league,
                         'user': user,
                         'invite': invite,
                         'site': current_site,
                         'profile': profile}
        message = render_to_string('email_league_invite.txt',
                                    email_context)        
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [user.email, ])

    def apply_to_league(self, league, user):
        league = League.objects.get(pk=league)
        application = LeagueJoinStates.objects.filter(league=league,
                                                      user=user)
        if application:
            application.get().apply_(originator=user)
        else:
            application = LeagueJoinStates(league=league,
                                           user=user,
                                           state=STATE_APPLIED)
            application.save()
        current_site = Site.objects.get_current()
        subject = "Application to join %s" % league.name
        profile =  RegistrationProfile.objects.filter(user=user).get()
        email_context = {'league': league,
                         'user': user,
                         'application': application,
                         'site': current_site,
                         'profile': profile}
        message = render_to_string('email_league_apply.txt',
                                    email_context)        
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [league.owner.email, ])
        

    def get_query_set(self):
        return super(LeagueJoinStatesManager, self)\
               .get_query_set()\
               .filter(state=STATE_ACCEPTED)


class LeagueJoinStates(Model):
    """Describes the mapping between Leagues and Users,
    """
    league = models.ForeignKey(League)
    user = models.ForeignKey(CustomUser)
    state = models.SmallIntegerField(choices=INVITE_STATES.items())
    date_assigned = models.DateTimeField(auto_now_add=True)

    joined = LeagueJoinStatesManager()
    objects = models.Manager()
    
    def apply_(self, originator=None):
        if self.state != STATE_DECLINED \
               or originator != self.user:
            raise self.InvalidStateTransition()
        self.state = STATE_APPLIED
        self.save()

    def accept(self, originator=None):
        if self.state not in (STATE_INVITED, STATE_ACCEPTED) \
               or originator != self.user:
            raise self.InvalidStateTransition()
        self.state = STATE_ACCEPTED
        self.save()
        
    def decline(self, originator=None):
        if self.state not in (STATE_INVITED, STATE_DECLINED) \
               or originator != self.user:
            raise self.InvalidStateTransition()
        self.state = STATE_DECLINED
        self.save()

    def reject(self, originator=None):
        if self.state not in (STATE_APPLIED,
                              STATE_ACCEPTED,
                              STATE_REJECTED) \
               or originator != self.league.owner:
            raise self.InvalidStateTransition()
        self.state = STATE_REJECTED
        self.save()

    def approve(self, originator=None):
        if self.state not in (STATE_APPLIED, STATE_ACCEPTED) \
               or originator != self.league.owner:
            raise self.InvalidStateTransition()
        self.state = STATE_ACCEPTED
        self.save()

    class InvalidStateTransition(Exception):
        pass


class Division(Model):
    name = models.CharField(max_length=60)
    def __unicode__(self):
        return "%s" % self.name

class Team(Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=80)
    division = models.ForeignKey(Division,
                                 blank=True,
                                 null=True)

    def __unicode__(self):
        return "%s" % self.name
    
    @permalink
    def get_absolute_url(self):
        return ("team", (self.slug,))


class LeagueTable(Model):
    name = models.CharField(max_length=80)
    teams = models.ManyToManyField(Team)
    year = models.DateField()
    added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "%s (%s)" % (self.name,
                            self.added.strftime("%y/%m/%d"))

    @property
    def ordered_teams(self):
        return self.teams.order_by('whatever_leaguetable_teams.id')

    def max_goal_diff(self, other_leaguetable):
        my_pos = 0
        diff = 0
        for team in self.ordered_teams:
            try:
                other_pos = list(other_leaguetable.ordered_teams)\
                            .index(team)
                diff += (other_pos - my_pos)**2
            except ValueError:
                pass
            my_pos += 1
        return diff

class Position(Model):
    position = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return str(self.position)

    def invert_position(self):
        return 0 - self.position

    class Meta:
        ordering = ['date']


class Fixture(Model):
    date = models.DateTimeField()
    home = models.ForeignKey(Team,
                             related_name="home_fixtures")
    away = models.ForeignKey(Team,
                             related_name="away_fixtures")

    def __unicode__(self):
        return "%s v. %s on %s" % (self.home.name,
                                   self.away.name,
                                   self.date.strftime("%d/%m"))

class CursorGenerator(object):
    def __init__(self,
                 cursor,
                 start_count=None,
                 max_count=None,
                 model_type=None):
        self.cursor = cursor
        self.start_count = start_count
        self.max_count = max_count
        self.model_type = model_type
        
    def __iter__(self):
        return self._get_predictions_from_cursor(self.cursor,
                                                 self.start_count,
                                                 self.max_count)
    def __getslice__(self, start, end):
        return self._get_predictions_from_cursor(self.cursor,
                                                 start_count=start,
                                                 max_count=end-start)

    def count(self):
        return self.cursor.rowcount
    
    def _get_predictions_from_cursor(self,
                                     cursor,
                                     start_count=None,
                                     max_count=None):
        curr_count = 0
        while True:
            next_row = cursor.fetchone()
            if not next_row:
                break
            d = {}
            for (i, column_desc) in enumerate(cursor.description):
                d[column_desc[0]] = next_row[i]
            prediction = self.model_type.objects.get(pk=d['id'])
            prediction.rank = d['rank']
            curr_count += 1
            if max_count and curr_count == start_count + max_count:
                break
            elif start_count and start_count > curr_count:
                continue
            else:
                yield prediction

class Competition(Model):
    name = models.CharField(max_length=80)
    teaser = models.CharField(max_length=180,
                              blank=True,
                              null=True)
    prize = models.CharField(max_length=180,
                             blank=True,
                             null=True)
    start_date = models.DateTimeField()
    close_date = models.DateTimeField()
    competition_date = models.DateTimeField()

    def __unicode__(self):
        return self.name

    def predictions_with_rank(self):
        SQL = """
        select id, user_id, score, goaldiff, competition_id, rank()
        over (partition by competition_id order by score desc,
        goaldiff desc, edited_date) from whatever_prediction where
        competition_id = %s order by competition_id, rank;
        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(SQL, [self.id,])
        return CursorGenerator(cursor, model_type=Prediction)
        
    @permalink
    def get_absolute_url(self):
        return ("competition", (self.id,))

    def is_open(self):
        now = datetime.datetime.now()
        return self.start_date < now < self.close_date

    def upcoming_fixtures(self):
        now = datetime.datetime.now()
        fixtures = Fixture.objects\
                   .filter(date__gt=now,
                           date__lt=self.competition_date)
        return fixtures

    def is_finished(self):
        now = datetime.datetime.now()
        return self.competition_date < now

    def time_left(self):
        now = datetime.datetime.now()
        return self.competition_date  - now

    def top_predictions(self):
        return self.prediction_set.all()[:10]

    def winner(self):
        p = self.prediction_set.all()
        p = p.count() and p[0] or None
        return p

    class Meta:
        ordering = ['competition_date']


class RunningScore(Model):
    name = models.CharField(max_length=80)
    user = models.ForeignKey(CustomUser)
    score = models.IntegerField(default=0)
    goaldiff = models.IntegerField(default=0)
    positions = models.ManyToManyField(Position)
    created_date = models.DateTimeField(auto_now_add=True)
    edited_date = models.DateTimeField(auto_now_add=True)
    competition = models.ForeignKey(Competition)

    @permalink
    def get_absolute_url(self):
        return ("runningscore", (self.slug,))

    @property
    def current_position(self):
        try:
            p = self.positions\
                .order_by('-date')\
                .all()[0].position
        except IndexError:
            p = 0
        return p

    @property
    def change_on_last_position(self):
        current = self.current_position
        try:
            last = self.positions\
                   .order_by('-date')\
                   .all()[1].position
        except IndexError:
            last = current
        return last - current

    @property
    def abs_change_on_last_position(self):
        return abs(self.change_on_last_position)
        
    def direction_change(self):
        pos = self.change_on_last_position
        if pos > 0:
            direction = "up"
        elif pos < 0:
            direction = "down"
        else:
            direction = ""
        return direction

    def calculateScore(self, new_score=0):
        if not settings.CLOSE_SEASON:
            self.score += round(new_score / 100.0)
            self.save()
        return self.score

    def calculateGoalDiff(self, new_goaldiff=0):
        if not settings.CLOSE_SEASON:
            self.goaldiff += round(new_goaldiff / 10.0)
            self.save()
        return self.goaldiff

    def calculatePosition(self, save=True):
        SQL = """
        select id, rank, user_id from
        (select id, user_id, score, goaldiff, competition_id, rank()
        over (partition by competition_id order by score desc,
        goaldiff desc, edited_date) from whatever_runningscore where
        competition_id = %s) as temp where user_id = %s;
        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(SQL, [self.competition.id,
                             self.user.id])
        prediction = list(CursorGenerator(cursor,
                                          model_type=RunningScore))[0]
        pos = prediction.rank
        if save:
            now = datetime.date.today()
            position = Position.objects.get_or_create(
                position=pos,
                date=now)[0]
            self.positions.add(position)
            self.save()
        return pos
    
    def in_context(self):
        predictions = RunningScore.objects.filter(competition=self.competition)
        predictions = predictions.order_by('-score',
                                           '-goaldiff',
                                           'created_date')    
        predictions = predictions.all()
        my_position = self.current_position
        predictions = predictions[max(0, my_position-4)\
                                  :min(my_position+5,predictions.count())]
        return predictions

    def in_facebook_context_with_rank(self):
        friends = self.user.facebookuser.get().friends.all()
        friend_ids = [self.user.id] + [x.user.id for x in friends]
        return self.in_context_with_rank(
            user_subset_ids=friend_ids,
            start_count=0)

    def in_context_with_rank(self,
                             user_subset_ids=None,
                             start_count=None):
        from django.db import connection
        if not user_subset_ids:
            SQL = """
            select id, user_id, score, goaldiff, competition_id, rank()
            over (partition by competition_id order by score desc,
            goaldiff desc, edited_date) from whatever_runningscore where
            competition_id = %s order by competition_id, rank;
            """
            cursor = connection.cursor()
            cursor.execute(SQL, [self.competition.id,])
        else:
            SQL_start = """
            select id, user_id, score, goaldiff, competition_id, rank()
            over (partition by competition_id order by score desc,
            goaldiff desc, edited_date) from whatever_runningscore where
            competition_id = %s
            """
            join_word = " AND "
            for user_id in user_subset_ids:
                SQL_start += join_word + "user_id = %s "
                join_word = " OR "

            SQL_start += " order by competition_id, rank"
            cursor = connection.cursor()
            args = [self.competition_id] + user_subset_ids
            cursor.execute(SQL_start, args)
        if start_count is None:
            start_count = max(0,self.current_position-5)

        return CursorGenerator(
            cursor,
            start_count=start_count,
            max_count=10,
            model_type=RunningScore
            )


    def __unicode__(self):
        return "%s %s (%s)" % (self.competition.name,
                               self.name,
                               self.created_date.strftime("%y/%m/%d"))

    class Meta:
        ordering = ('-score', '-goaldiff', 'edited_date')



class Prediction(Model):
    name = models.CharField(max_length=80)
    teams = models.ManyToManyField(Team)
    year = models.DateField(blank=True,
                            null=True)
    user = models.ForeignKey(CustomUser)
    score = models.IntegerField(default=0)
    goaldiff = models.IntegerField(default=0)
    positions = models.ManyToManyField(Position)
    created_date = models.DateTimeField(auto_now_add=True)
    edited_date = models.DateTimeField(auto_now_add=True)
    needs_update = models.BooleanField(default=True)
    needs_ordering = models.BooleanField(default=True)
    last_used_table = models.ForeignKey(LeagueTable,
                                        blank=True,
                                        null=True)
    last_used_goaldiff_table = \
                models.ForeignKey(LeagueTable,
                                  blank=True,
                                  null=True,
                                  related_name='predictions_for_goaldiff')
    competition = models.ForeignKey(Competition)
    included_in_meta_competition = models.BooleanField(default=False)
    
    @permalink
    def get_absolute_url(self):
        return ("prediction", (self.slug,))

    @property
    def ordered_teams(self):
        return self.teams.order_by('whatever_prediction_teams.id')

    def decorated_teams(self):
        """Return the teams with an indicator of how far off they are
        """
        decorated = []
        current_table = getCurrentTable()
        count = 0
        for team in self.ordered_teams.all():
            other = list(current_table.ordered_teams.all()).index(team)
            diff = abs(other-count)
            team.diff = diff
            count += 1
            decorated.append(team)
        return decorated
    
    @property
    def current_position(self):
        try:
            p = self.positions\
                .order_by('-date')\
                .all()[0].position
        except IndexError:
            p = 0
        return p

    @property
    def change_on_last_position(self):
        current = self.current_position
        try:
            last = self.positions\
                   .order_by('-date')\
                   .all()[1].position
        except IndexError:
            last = current
        return last - current

    @property
    def abs_change_on_last_position(self):
        return abs(self.change_on_last_position)
        
    def direction_change(self):
        pos = self.change_on_last_position
        if pos > 0:
            direction = "up"
        elif pos < 0:
            direction = "down"
        else:
            direction = ""
        return direction

    def calculateScore(self, force=False):
        if settings.CLOSE_SEASON:
            current_table = getPreviousTable(
                competition=self.competition)
        else:
            current_table = getCurrentTable()
        score = 0
        if force or self.needs_update or current_table != self.last_used_table:
            count = 0
            score = 0
            spot_on = 0
            one_off = 0
            two_off = 0
            for item in self.ordered_teams.all():
                try:
                    other = list(current_table.ordered_teams.all())\
                            .index(item)
                except ValueError:
                    if settings.CLOSE_SEASON:
                        other = 21
                    else:
                        raise
                diff = abs(other-count)
                count += 1
                if diff > 2:
                    continue
                elif diff == 0:
                    spot_on += 1
                elif diff == 1:
                    one_off += 1
                elif diff == 2:
                    two_off += 1
            self.spot_on = spot_on
            self.one_off = one_off
            self.two_off = two_off
            score =  int(round(23.4 * (spot_on * math.log(137,10) + \
                                 one_off * math.log(11,10) + \
                                 two_off * math.log(3,10))))
            self.score = score
            self.user.current_score = score
            self.user.save()
            self.last_used_table = current_table
            self.needs_ordering = True
            self.save()
        return score

    def calculateGoalDiff(self, force=False):
        guessed_pos = 0
        score = 0
        lyeos = getPreviousTable(competition=self.competition)
        current_table = getCurrentTable()
        if force or self.needs_update \
               or current_table != self.last_used_goaldiff_table:
            for item in self.ordered_teams:
                current_pos = list(current_table.ordered_teams)\
                              .index(item)
                try:
                    last_year_pos = list(lyeos.ordered_teams).index(item)
                except ValueError:
                    last_year_pos = 21
                if guessed_pos == current_pos:
                    diff = (last_year_pos - guessed_pos)**2
                    score += diff
                elif abs(current_pos - guessed_pos) == 1:
                    score += abs(last_year_pos - guessed_pos)
                guessed_pos += 1
            self.goaldiff = score
            self.last_used_goaldiff_table = current_table
            self.needs_ordering = True
            self.save()
        return self.needs_ordering

    def calculatePosition(self, save=True):
        SQL = """
        select id, rank, user_id from
        (select id, user_id, score, goaldiff, competition_id, rank()
        over (partition by competition_id order by score desc,
        goaldiff desc, edited_date) from whatever_prediction where
        competition_id = %s) as temp where user_id = %s;
        """
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(SQL, [self.competition.id,
                             self.user.id])
        prediction = list(CursorGenerator(cursor,
                                          model_type=Prediction))[0]
        pos = prediction.rank
        if save:
            now = datetime.date.today()
            position = Position.objects.get_or_create(
                position=pos,
                date=now)[0]
            self.positions.add(position)
            self.needs_ordering = False
            self.save()
        return pos
    
    def calculateApproxPosition(self):
        delta = 0
        all_predictions = Prediction.objects\
                          .filter(competition=self.competition)
        max_delta = 1000
        step = int(max_delta/10.0) + 1
        now = datetime.date.today()
        delta = 0
        while delta <= max_delta:
            matches = Prediction.objects\
                    .filter(competition=self.competition,
                            score__range=(self.score-delta,
                                          self.score+delta))\
                    .exclude(pk=self.pk)
            if matches.count():
                for match in matches:
                    if match.score < self.score:
                        position = Position.objects\
                                   .get_or_create(position=match.current_position-1,
                                                  date=now)[0]
                        self.positions.add(position)
                        self.save()
                        return self.current_position
            delta += 1
        pos = all_predictions.count()
        position = Position.objects.get_or_create(position=pos,
                                                  date=now)[0]
        self.positions.add(position)
        self.needs_ordering = True
        self.save()
        return self.current_position

    def in_context(self):
        predictions = Prediction.objects.filter(competition=self.competition)
        predictions = predictions.order_by('-score',
                                           '-goaldiff',
                                           'created_date')    
        predictions = predictions.all()
        my_position = self.current_position
        predictions = predictions[max(0, my_position-4)\
                                  :min(my_position+5,predictions.count())]
        return predictions

    def in_facebook_context_with_rank(self):
        friends = self.user.facebookuser.get().friends.all()
        friend_ids = [self.user.id] + [x.user.id for x in friends]
        return self.in_context_with_rank(
            user_subset_ids=friend_ids,
            start_count=0)
        
    def in_context_with_rank(self,
                             user_subset_ids=None,
                             start_count=None):
        from django.db import connection
        if not user_subset_ids:
            SQL = """
            select id, user_id, score, goaldiff, competition_id, rank()
            over (partition by competition_id order by score desc,
            goaldiff desc, edited_date) from whatever_prediction where
            competition_id = %s order by competition_id, rank;
            """
            cursor = connection.cursor()
            cursor.execute(SQL, [self.competition.id,])
        else:
            SQL_start = """
            select id, user_id, score, goaldiff, competition_id, rank()
            over (partition by competition_id order by score desc,
            goaldiff desc, edited_date) from whatever_prediction where
            competition_id = %s 
            """
            join_word = " AND ("
            for user_id in user_subset_ids:
                SQL_start += join_word + " user_id = %s "
                join_word = " OR "
            SQL_start += ") order by competition_id, rank"
            cursor = connection.cursor()
            args = [self.competition_id] + user_subset_ids
            cursor.execute(SQL_start, args)
        if start_count is None:
            start_count = max(0,self.current_position-5)
        return CursorGenerator(
            cursor,
            start_count=start_count,
            max_count=15,
            model_type=Prediction
            )


    def __unicode__(self):
        return "%s %s (%s): %s " % (self.competition.name,
                                    self.name,
                                    self.created_date.strftime("%y/%m/%d"),
                                    ", ".join([x.name for x in self.ordered_teams.all()]))

    class Meta:
        ordering = ('-score', '-goaldiff', 'edited_date')
    
class RegistrationManager(models.Manager):
    """
    The methods defined here provide shortcuts for account creation
    and activation (including generation and emailing of activation
    keys), and for cleaning out expired inactive accounts.
    
    """
    def activate_user(self, activation_key):
        """
        Validate an activation key and activate the corresponding
        ``User`` if valid.
        """
        # Make sure the key we're trying conforms to the pattern of a
        # SHA1 hash; if it doesn't, no point trying to look it up in
        # the database.
        profile = self.get_user(activation_key,
                                only_activated=False)
        if profile and not profile.activated and \
               not profile.activation_key_expired():
            user = profile.user
            user.is_active = True
            user.save()
            profile.activated = True
            profile.save()
            return profile
        else:
            return False

    def get_user(self, activation_key, only_activated=True):
        profile = None
        if SHA1_RE.search(activation_key):
            profile = RegistrationProfile.objects.all()\
                      .filter(activation_key=activation_key)
            if only_activated:
                profile = profile.filter(activated=True)
            if profile:
                profile = profile[0]
        return profile
        
    def create_profile(self,
                       user,
                       email=True):
        salt = sha.new(str(random.random())).hexdigest()[:5]
        activation_key = sha.new(salt+user.username).hexdigest()
        profile = RegistrationProfile(user=user,
                                      email=user.email,
                                      activation_key=activation_key)
        profile.save()

        user.is_active = False
        user.save()
        if email:
            profile.send_activation_email()
        return profile
    
        
    def delete_expired_users(self):
        for profile in RegistrationProfile.all():
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_active:
                    user.delete()
                    profile.delete()

class EmailMessage(Model):
    subject = models.CharField(max_length=80)
    body = models.TextField(blank=True,
                            null=True)
    recipient = models.ForeignKey(CustomUser)
    date_sent = models.DateTimeField(blank=True,
                                     null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def get_body(self):
        lines = list(self.lines.all())
        joined = []
        i = 1
        for line in lines:
            joined.append(line.line)
            if i == len(lines):
                if i == 1:
                    break
                else:
                    joined.append(" and ")
            else:
                joined.append(", ")
        joined.append(".")
        joined_lines = "".join(joined)                     
        return "%s\n\n%s" % (self.body, joined_lines)

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ('date_created',)


class EmailUpdateLines(Model):
    line = models.CharField(max_length=180)
    email = models.ForeignKey(EmailMessage,
                              related_name='lines')


class RegistrationProfile(Model):
    """
    A simple profile which stores an activation key for use in passwordless
    site interaction

    """
    user = models.ForeignKey(CustomUser,
                             verbose_name='user')
    email = models.CharField(max_length=80)
    activation_key = models.CharField(max_length=50)
    objects = RegistrationManager()
    activated = models.BooleanField(default=False)
   
    class Meta:
        verbose_name = 'registration profile'
        verbose_name_plural = 'registration profiles'
    
    def __unicode__(self):
        return u"Registration information for %s" % self.user
    
    def activation_key_expired(self):
        expiration_date = datetime.timedelta(
            days=settings.ACCOUNT_ACTIVATION_DAYS)
        return not self.activated and \
               (self.user.date_joined + expiration_date <= datetime.datetime.now())
    activation_key_expired.boolean = True

    def send_activation_email(self):
        current_site = Site.objects.get_current()
        subject = "Please confirm your registration"
        email_context = {'activation_key': self.activation_key,
                         'site': current_site,
                         'user': self.user}
        message = render_to_string('activation_email.txt',
                                   email_context)
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email,])

    def send_reset_password_email(self):
        current_site = Site.objects.get_current()
        subject = "Your What Ever Trevor password"
        email_context = {'activation_key': self.activation_key,
                         'site': current_site,
                         'user': self.user}
        message = render_to_string('reset_password_email.txt',
                                   email_context)
        send_mail(subject,
                  message,
                  settings.DEFAULT_FROM_EMAIL,
                  [self.user.email,])

def getCurrentTable():
    try:
        return LeagueTable.objects\
               .filter(name=settings.CURRENT_LEAGUE_ID)\
               .order_by("-added")\
               .all()[0]
    except IndexError:
        table = None
    return table

def getPreviousTable(competition=None):
    """Returns the last table before the specified
    competition started
    """
    if not competition:
        competition = Competition.objects.get(
            pk=settings.PREVIOUS_COMPETITION_ID)
    date = competition.start_date
    tables = LeagueTable.objects\
             .filter(added__lt=date)\
             .order_by("-added")\
             .all() 
    return tables and tables[1] or None

def queue_movement_email(sender, **kwargs):
    prediction = kwargs['prediction']
    email, created = EmailMessage.objects\
                     .get_or_create(subject="Regular email update",
                                    recipient=prediction.user,
                                    date_sent__isnull=True)
    message = "%s %s places in '%s'" % \
              (prediction.direction_change(),
               prediction.abs_change_on_last_position,
               prediction.competition.name)
    line = EmailUpdateLines.objects\
           .create(line="You moved " + message,
                   email=email)

    if created:
        email.lines.add(line)

    else:
        email.lines.add(line)
    email.save()
        
position_changed.connect(queue_movement_email)

def date_joined_histogram(previous_days=120):
    from django.db import connection
    sql = ("SELECT to_char(auth_user.date_joined, 'DD Mon') AS shortdate, "
           "COUNT(*), DATE_TRUNC('day', auth_user.date_joined) AS date "
           "FROM auth_user WHERE is_active = True "
           "AND auth_user.date_joined > now() - interval '%s days' "
           "GROUP BY date, shortdate "
           "ORDER BY date;")
    cursor = connection.cursor()
    cursor.execute(sql, [previous_days])
    return cursor

def date_logged_in_histogram(previous_days=120):
    from django.db import connection
    sql = ("SELECT to_char(auth_user.last_login, 'DD Mon') AS shortdate, "
           "COUNT(*), DATE_TRUNC('day', auth_user.last_login) AS date "
           "FROM auth_user WHERE is_active = True "
           "AND auth_user.last_login > now() - interval '%s days' "
           "GROUP BY date, shortdate "
           "ORDER BY date;")
    cursor = connection.cursor()
    cursor.execute(sql, [previous_days])
    return cursor
