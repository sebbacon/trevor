from datetime import datetime, timedelta

from django import template
from django.db.models.query import QuerySet
from django.template import Node, NodeList, Variable, VariableDoesNotExist
from django.template import TemplateSyntaxError

register = template.Library()
 
MOMENT = 120    # duration in seconds within which the time difference 
                # will be rendered as 'a moment ago'

@register.filter
def percentage(fraction, population):
    """Usage: {{ fraction|percentage:'population' }}
    """
    try:  
        return "%.0f%%" % ((float(fraction) / float(population)) * 100)  
    except (ValueError, ZeroDivisionError):  
        return ""

@register.filter
def googleometerpos(fraction, population):
    """Usage: {{ fraction|percentage:'population' }}
    """
    if fraction == 1:
        return 100
    try:  
        amount = 100 - int(((float(fraction) / float(population)) * 100))
        return amount
    except (ValueError, ZeroDivisionError):  
        return 0

@register.filter
def ordinalise(value):
    value = str(value)
    suffix = "th"
    if value.endswith("1"):
        suffix = "st"
    elif value.endswith("2"):
        suffix = "nd"
    elif value.endswith("3"):
        suffix = "rd"
    return value + suffix
        
@register.filter
def naturalTimeDifference(value):
    """Finds the difference between the datetime value given and now()
    and returns appropriate humanize form
    """

    if isinstance(value, timedelta):
        delta = value
    elif isinstance(value, datetime):
        delta = datetime.now() - value        
    else:
        delta = None

    if delta:
        if delta.days > 6:
            return value.strftime("%b %d") # May 15
        if delta.days > 1:
            return value.strftime("%A") # Wednesday
        elif delta.days == 1:
            return 'yesterday'
        elif delta.seconds >= 7200:
            return str(delta.seconds / 3600 ) + ' hours ago'
        elif delta.seconds >= 3600:
            return '1 hour ago' 
        elif delta.seconds > MOMENT:
            return str(delta.seconds/60) + ' minutes ago' 
        else:
            return 'a moment ago' 
    else:
        return str(value)

@register.filter
def naturalTimeDifferenceDays(value):
    """Finds the difference between the datetime value given and now()
    and returns appropriate humanize form
    """

    if isinstance(value, timedelta):
        delta = value
    elif isinstance(value, datetime):
        delta = datetime.now() - value        
    else:
        delta = None

    if delta:
        if delta.days > 1:
            return "%s days ago" % delta.days
        elif delta.days == 1:
            return 'yesterday'
        elif delta.seconds >= 7200:
            return str(delta.seconds / 3600 ) + ' hours ago'
        elif delta.seconds >= 3600:
            return '1 hour ago' 
        elif delta.seconds > MOMENT:
            return str(delta.seconds/60) + ' minutes ago' 
        else:
            return 'a moment ago' 
    else:
        return str(value)

@register.filter
def naturalTimeDifferenceFuture(value):
    """Finds the difference between the datetime value given and now()
    and returns appropriate humanize form
    """

    if isinstance(value, timedelta):
        delta = value
    elif isinstance(value, datetime):
        delta = value - datetime.now()
    else:
        delta = None

    if delta:
        if delta.days > 1:
            return "in %s days" % delta.days
        elif delta.days == 1:
            return 'tomorrow'
        elif delta.seconds >= 7200:
            return "in %s hours" % str(delta.seconds / 3600 ) 
        elif delta.seconds >= 3600:
            return "in 1 hour" 
        elif delta.seconds > MOMENT:
            return "in %s minutes" % str(delta.seconds/60) 
        else:
            return "a moment" 
    else:
        return str(value)

class IfInNode(Node): 
    def __init__(self, nodelist_in, nodelist_not_in, element_var, sequence_var): 
        self.nodelist_in = nodelist_in 
        self.nodelist_not_in = nodelist_not_in 
        self.element_var = Variable(element_var) 
        self.sequence_var = Variable(sequence_var) 
 
    def render(self, context): 
        try: 
            element = self.element_var.resolve(context) 
            sequence = self.sequence_var.resolve(context) 
        except VariableDoesNotExist: 
            return self.nodelist_not_in.render(context) 
        if isinstance(sequence, QuerySet): 
            # QuerySets are checked at the database level, 
            # by comparing primary keys 
            if not hasattr(element, 'pk'): 
                return self.nodelist_not_in.render(context) 
            if sequence.filter(pk=element.pk).count() > 0: 
                return self.nodelist_in.render(context) 
            else: 
                return self.nodelist_not_in.render(context) 
        if (element in sequence): 
            return self.nodelist_in.render(context) 
        else: 
            return self.nodelist_not_in.render(context) 
  
 
@register.tag 
def ifin(parser, token): 
    """ 
    Checks if element is present in the sequence. 
 
    {% ifin element sequence %} 
        Element is in sequence 
    {% else %} 
        Element is in sequence... not! 
    {% endifin %} 
    """ 
    try: 
        tag_name, element_var, sequence_var = token.split_contents() 
    except ValueError: 
        raise TemplateSyntaxError
    nodelist_in = parser.parse(('endifin', 'else')) 
    token = parser.next_token() 
    if token.contents == 'else': 
        nodelist_not_in = parser.parse(('endifin',)) 
        parser.delete_first_token() 
    else: 
        nodelist_not_in = NodeList() 
    return IfInNode(nodelist_in, nodelist_not_in, element_var, sequence_var) 
 
@register.tag 
def ifnotin(parser, token): 
    """ 
    Checks if element is not present in the sequence. 
 
    {% ifnotin element sequence %} 
        Element is in sequence... not! 
    {% else %} 
        Element is in sequence 
    {% endifnotin %} 
    """ 
    try: 
        tag_name, element_var, sequence_var = token.split_contents() 
    except ValueError: 
        raise TemplateSyntaxError
    nodelist_not_in = parser.parse(('endifnotin','else')) 
    token = parser.next_token() 
    if token.contents == 'else': 
        nodelist_in = parser.parse(('endifnotin',)) 
        parser.delete_first_token() 
    else: 
        nodelist_in = NodeList() 
    return IfInNode(nodelist_in, nodelist_not_in, element_var, sequence_var) 

