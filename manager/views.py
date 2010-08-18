import csv

from django.http import HttpResponseRedirect as redirect
from django.core.urlresolvers import reverse
from django.http import HttpResponse

from django.contrib import messages

from utils import render
from whatever.models import date_joined_histogram
from whatever.models import date_logged_in_histogram
from whatever.models import CustomUser
from whatever.models import Prediction
import settings

from campaign_monitor_api import CampaignMonitorApi


@render('index.html')
def index(request):
    return locals()

def user_csv(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] =\
                    'attachment; filename=trevorusers.csv'
    if request.user.is_superuser:
        writer = csv.writer(response)
        for user in CustomUser.objects.filter(is_active=True,
                                              can_email=True):
            name = "%s %s" % (user.first_name, user.last_name)
            try:
                main_prediction = Prediction.objects.get(
                    user=user,
                    competition__id=settings.CURRENT_COMPETITION_ID)
            except Prediction.DoesNotExist:
                continue
            abs_change = main_prediction.abs_change_on_last_position
            change_words = "%s %s place" % \
                           (main_prediction.direction_change(),
                            abs_change)
            if abs_change != 1:
                change_words += "s"

            writer.writerow([
                name,
                user.email,
                main_prediction.change_on_last_position,
                change_words,
                user.last_login])
    return response

@render('campaignmonitor.html')
def campaignmonitor(request):
    if not request.user.is_superuser:
        return locals()
    if request.method == "POST" and request.POST.get('export'):
        success = failure = []
        mailable_users = CustomUser.objects.filter(can_email=True,
                                                   is_active=True)        
        cm = CampaignMonitorApi(settings.CAMPAIGN_MONITOR_KEY, None)
        for user in mailable_users:
            try:
                done = cm.subscriber_add(settings.CAMPAIGN_MONITOR_LIST,
                                         user.email,
                                         "%s %s" % (user.first_name,
                                                    user.last_name))
                if done:
                    success.append(user.email)
                else:
                    failure.append(user.email)
            except CampaignMonitorApi.CampaignMonitorApiException:
                failure.append("* " + user.email)
        messages.info(request,
                      "%s new emails imported" % len(success))
        if failure:
            messages.error(request,
                           "Problem importing %s" % len(failure))
    return locals()

@render('statistics.html')
def statistics(request):
    joined_histogram = date_joined_histogram()
    logged_in_histogram = date_logged_in_histogram()
    return locals()

# we all said it'd be the last critical list
# at first thought it was them taking note of other things that are
# very important

