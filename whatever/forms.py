import datetime
import re

from django import forms
from django.forms.formsets import formset_factory 
from django.template import Context, loader
from models import Prediction
from models import Team
from models import RegistrationProfile
from models import CustomUser
from django.forms.widgets import CheckboxSelectMultiple
from django.forms.widgets import MultipleHiddenInput
from django.forms.fields import ChoiceField
from django.forms.util import ValidationError
from django.utils.encoding import smart_unicode
from django.http import QueryDict

import settings
from utils import getCurrentTable
from widgets import HiddenSelectMultiple
from widgets import TeamSelection
from whatever.models import League
from whatever.models import Competition
from whatever.models import RunningScore

POSTCODE_RE = re.compile(r'\b[A-PR-UWYZ][A-HK-Y0-9][A-HJKSTUW0-9]?[ABEHMNPRVWXY0-9]? {0,2}[0-9][ABD-HJLN-UW-Z]{2}\b',re.I)

class TemplatedForm(forms.Form):
    def output_via_template(self):
        "Helper function for fieldsting fields data from form."
        bound_fields = [forms.forms.BoundField(self, field, name) for name, field \
                        in self.fields.items()]
        c = Context(dict(form = self, bound_fields = bound_fields))
        t = loader.get_template('forms/form.html')
        return t.render(c)

    def as_table(self):
        return self.output_via_template()

    def full_clean(self):
        "Strip whitespace automatically in all form fields"
        data = self.data.copy()
        for k, vs in self.data.lists():
            new_vs = []
            for v in vs:
                new_vs.append(v.strip())
            data.setlist(k, new_vs)
        self.data = data
        super(TemplatedForm, self).full_clean()
            
class ListField(ChoiceField):
    """A field that returns a list of values, but doesn't care if
    they're in a predefined set of choices (like
    MultipleChoiceField). 
    """
    hidden_widget = MultipleHiddenInput
    widget = CheckboxSelectMultiple
    default_error_messages = {
        'invalid_list': 'Enter a list of values.',
    }

    def clean(self, value):
        """
        Validates that the input is a list or tuple.
        """
        if self.required and not value:
            raise ValidationError(self.error_messages['required'])
        elif not self.required and not value:
            return []
        if not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'])
        new_value = [smart_unicode(val) for val in value]
        return new_value


class NewPasswordForm(TemplatedForm):
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=True,
                                label="Give yourself a password")
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=True,
                                label="Repeat password")
    
    def clean(self):
        if 'password1' in self.cleaned_data \
               and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] \
                   != self.cleaned_data['password2']:
                raise forms.ValidationError('You must type the same '
                                            'password each time')
        return self.cleaned_data


class PredictionForm(TemplatedForm):
    _choices = [(t.id, t.name) for t in getCurrentTable()\
                .teams.all().order_by('name')]
    prediction = forms.MultipleChoiceField(label="",
                                           choices=_choices,
                                           widget=HiddenSelectMultiple)

    def __init__(self, *args, **kw):
        default_table = kw.pop('default_table', None)
        if not default_table:
            default_table = getCurrentTable()
        super(PredictionForm, self).__init__(*args, **kw)
        choices = [(t.id, t.name) for t in default_table\
                   .ordered_teams.all()]
        self.fields['prediction'].choices = choices

    def save(self, domain_override=""):
        return self.cleaned_data['prediction']


class PredictionPasswordForm(PredictionForm, NewPasswordForm):
    pass

def _setup_initial_prediction(user, prediction, competition):
    this_year = datetime.datetime(settings.CURRENT_SEASON, 1, 1)
    if not Prediction.objects.filter(year=this_year,
                                     user=user,
                                     competition=competition)\
                             .count():        
        prediction_obj = Prediction(year=this_year,
                                    user=user,
                                    name=user.email,
                                    competition=competition)
        prediction_obj.save()

        for t_id in prediction:
            prediction_obj.teams.add(Team.objects.get(pk=t_id))
        prediction_obj.save()
        prediction_obj.calculateScore()
        prediction_obj.calculateGoalDiff()
        prediction_obj.calculatePosition()
        meta_competition = Competition.objects.get(
            pk=settings.CURRENT_META_COMPETITION_ID)
        runningscore = RunningScore.objects.create(
            name="Running score",
            user=user,
            competition=meta_competition)


class UserForm(TemplatedForm):
    first_name = forms.CharField(required=False,
                                 help_text="""Think! Prize winners are
    required to verify name by passport, driving license or birth
    certificate.  See our terms and conditions for full details""")
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True, max_length=75)
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=True,
                                label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=True,
                                label="Repeat password")
    can_email = forms.BooleanField(label="",
                                   help_text=("I want the inside scoop - please send me email updates!"),
                                   required=False,
                                   initial=True)
    supported_team = forms.ChoiceField(label="Which team do you support? (select one)",
                                       choices=TeamSelection.team_choices(),
                                       widget=TeamSelection,
                                       required=False)

    def clean(self):
        if 'password1' in self.cleaned_data \
               and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] \
                   != self.cleaned_data['password2']:
                raise forms.ValidationError('You must type the same '
                                            'password each time')
        return self.cleaned_data        
                                
    def clean_email(self):
        """
        Validate that the email is not already in use.
        
        """
        user = CustomUser.objects.all()\
               .filter(email=self.cleaned_data['email'].lower())
        if user:
            raise forms.ValidationError('This email is already registered')
        return self.cleaned_data['email'].lower()

    def save(self, domain_override="", prediction="", competition=""):
        """
        Create the new ``User`` and ``RegistrationProfile``, and
        returns the ``User`` (by calling
        ``RegistrationProfile.objects.create_inactive_user()``).
        
        """
        email = self.cleaned_data['email']
        can_email = self.cleaned_data['can_email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        password = self.cleaned_data['password1']
        supported_team_id = self.cleaned_data['supported_team']
        if supported_team_id and supported_team_id != "None":
            supported_team = Team.objects.get(pk=supported_team_id)
        else:
            supported_team = None
        this_year = datetime.datetime(settings.CURRENT_SEASON, 1, 1)
        user = CustomUser.objects.create(username=email,
                                         email=email,
                                         password=password,
                                         can_email=can_email,
                                         first_name=first_name,
                                         last_name=last_name,
                                         supported_team=supported_team,
                                         is_active=False)
        user.set_password(password)
        user.save()
        _setup_initial_prediction(user, prediction, competition)
        profile = RegistrationProfile.objects.create_profile(user)
        return profile


class MemberForm(TemplatedForm):
    email = forms.EmailField(required=True,
                             max_length=75,
                             label="Invite email address")
    def clean_email(self):
        return self.cleaned_data['email'].lower()
        
class LeagueForm(TemplatedForm):
    join_leagues = ListField(required=False)
    members = formset_factory(MemberForm,
                              extra=10,
                              can_delete=False)

    def __init__(self, *args, **kw):
        self.members = self.members(*args, **kw)
        return super(LeagueForm, self).__init__(*args, **kw)

    def clean(self):
        emails = [x for x in self.members.cleaned_data if x]
        if not emails:
            raise forms.ValidationError("You must supply at least one email")
        return self.cleaned_data
    
    def is_valid(self):
        return self.members.is_valid() \
               and super(LeagueForm, self).is_valid()


class NewLeagueForm(LeagueForm):
    name = forms.CharField(required=True,
                           max_length=16,
                           label='Give the league a name',
                           help_text="(max 16 characters)")    

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if League.objects.filter(name=name):
            error = "A league called %s already exists" % name
            raise forms.ValidationError(error)
        return self.cleaned_data['name']

