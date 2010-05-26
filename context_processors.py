from django.contrib.flatpages.models import FlatPage
import settings

def flatpages(request):
    context = {}
    pages = FlatPage.objects.all()
    context['pages'] = pages
    return context

def debug(request):
    context = {}
    context['DEBUG'] = settings.DEBUG
    context['OFFLINE'] = settings.OFFLINE
    return context

def include_settings(request):
    context = {}
    context['settings'] = settings
    return context
