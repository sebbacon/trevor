import os

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from whatever.models import Prediction
from utils import getThisYear

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not args or (args and args[0] not in ('load')):
            raise CommandError("USAGE: ./manage.py %s load" % \
                    os.path.basename(__file__).split('.')[0])



        predictions = Prediction.objects.filter(year=getThisYear(),
                                                user__facebookuser__isnull=False)
        fb = request.facebook
        for prediction in predictions:
            change = prediction.change_on_last_position
            if change == 0:
                continue
            message = "@:%s just moved %s %d places in WhatEverTrevor's league"
            direction = change > 0 and "up" or "down"
            amount = abs(change)
            uid = prediction.user.facebookuser_set.get().uid
            message = message % (uid, direction, amount)
            news = [{'message':message}]
            print fb.dashboard.addNews(news,
                                       uid=uid)
            print fb.stream.publish(message,
                                    uid=uid)

