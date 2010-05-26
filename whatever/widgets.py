from django import forms
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe

from itertools import cycle
from itertools import chain

from models import Team
from models import Division

class HiddenSelectMultiple(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = [x[0] for x in self.choices]
        choice_dict = {}
        for num, label in self.choices:
            choice_dict[num] = label
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ol id="prediction">']
        int_values = [int(v) for v in value]
        odd_or_even = cycle(['odd', 'even'])
        li_template = u'<li><label class="handle %s"%s>%s %s</label></li>'
        for i, v in enumerate(int_values):
            option_label = choice_dict[v]
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''
            field = forms.HiddenInput(attrs=final_attrs)
            option_value = force_unicode(v)
            rendered_field = field.render(name, option_value)
            option_label = conditional_escape(force_unicode(option_label))
            output.append(li_template % \
                          (odd_or_even.next(),
                           label_for,
                           rendered_field,
                           option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
    id_for_label = classmethod(id_for_label)

       
class TeamSelection(forms.Widget):
    """Output two dropdowns, one a filter, the second a complete
    list.  Include in the second an attribute that we can use to
    filter using the first dropdown.

    The filter and the dependent list are expressed as
    dependent_choices = \
         {(filter-id, filter-name): \
           list((dependent-id, dependent-name)}
    
    """

    def __init__(self, attrs=None, choices=()):
        super(TeamSelection, self).__init__(attrs)
        # choices can be any iterable, but we may need to render this widget
        # multiple times. Thus, collapse it into a list so it can be consumed
        # more than once.
        self.choices = list(choices)
        division_order = ['Premier League',
                          'Championship',
                          'League One',
                          'League Two',
                          'Conference']
        self.divisions = []
        for d in division_order:
            division = Division.objects.get(name=d)
            self.divisions.append((division.pk, division.name))


    @staticmethod
    def team_choices():
        teams = Team.objects.order_by('name').all()
        return [(t.pk, t.name) for t in teams]

    def choices_dict(self):
        mydict = {}
        divisions = Division.objects.all()
        for division in divisions:
            teams = [(t.pk, t.name) for t in division.team_set.all()]
            mydict[(division.pk, division.name)] = teams
        return mydict

    def render(self, name, value, attrs=None):
        choices = self.choices_dict()
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        teams_output = [u'<select%s>' % forms.util.flatatt(final_attrs)]
        divisions_output = [u'<select id="team_division">']
        for division, teams in choices.items():
            team_options = self.render_team_options(division, teams, [value])
            if team_options:
                teams_output.append(team_options)
        teams_output.append('</select>')
        division_options = self.render_division_options(self.divisions)
        if division_options:
            divisions_output.append(division_options)
        divisions_output.append('</select>')
        return mark_safe("Division:<br />")\
               + mark_safe(u'\n'.join(divisions_output))\
               + mark_safe("<br />")\
               + mark_safe("Club:<br />")\
               + mark_safe(u'\n'.join(teams_output))

    def render_team_options(self, division, teams, selected_teams):
        def render_option(option_value, option_label):
            option_value = force_unicode(option_value)
            selected_html = (option_value in selected_teams) and u' selected="selected"' or ''
            return u'<option class="%s" value="%s"%s>%s</option>' % (
                "division-%d" % division[0],
                escape(option_value), selected_html,
                conditional_escape(force_unicode(option_label)))
        # Normalize to strings.
        selected_teams = set([force_unicode(v) for v in selected_teams])
        output = []
        for option_value, option_label in chain(teams):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label))
        return u'\n'.join(output)

    def render_division_options(self, choices):
        def render_option(option_value, option_label):
            option_value = force_unicode(option_value)
            return u'<option value="%s">%s</option>' % (
                escape(option_value), 
                conditional_escape(force_unicode(option_label)))
        # Normalize to strings.
        output = []
        for option_value, option_label in chain(choices):
            if isinstance(option_label, (list, tuple)):
                output.append(u'<optgroup label="%s">' % escape(force_unicode(option_value)))
                for option in option_label:
                    output.append(render_option(*option))
                output.append(u'</optgroup>')
            else:
                output.append(render_option(option_value, option_label))
        return u'\n'.join(output)
