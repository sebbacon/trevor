import time
import datetime

from django.core.management.base import NoArgsCommand

from whatever import models
from whatever.signals import position_changed
from utils import getThisYear


def getOrMakePosition(n):
    try:
        p = models.Position.objects.get(position=n)
    except models.Position.DoesNotExist:
        p = models.Position(position=n)
        p.save()
    return p

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        start = time.time()
        this_year = getThisYear()

        predictions = models.Prediction.objects
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(1)
        predictions = predictions.filter(
            competition__start_date__lt=now,
            competition__competition_date__gt=yesterday)
        count = 0
        done = False
        for p in predictions.all():
            score = p.calculateScore()            
            p.calculateGoalDiff()
            p.needs_update = False
            p.save()
            count += 1
        date = datetime.date.today()
        current = models.getCurrentTable()
        for comp in models.Competition.objects\
                .filter(competition_date__gt=now):
            if comp.prediction_set\
                   .filter(needs_ordering=True).count():
                position = 1
                for p in comp.prediction_set.all():
                    pos, created = models.Position.objects\
                                   .get_or_create(position=position,
                                                  date=date)
                    p.positions.add(pos)
                    if p.abs_change_on_last_position > 0:
                        position_changed.send(sender=None,prediction=p)
                    p.needs_ordering = False
                    p.save()
                    position += 1
        if done:
            print "Calculated %d scores in %f seconds" % (count, time.time() - start)
            print "(%f per second)" % (count/(time.time()-start))
