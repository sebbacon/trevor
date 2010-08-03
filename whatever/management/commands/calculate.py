import time
import datetime

from django.core.management.base import NoArgsCommand

from whatever import models
from whatever.signals import position_changed
from utils import getThisYear
import settings

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
        # we are going to run calculation for all competitions that
        # have started, and the date of the competition is after
        # yesterday
        predictions = predictions.filter(
            competition__start_date__lt=now,
            competition__competition_date__gt=yesterday).all()
        count = 0
        done = False
        meta_competition = models.Competition.objects.get(
            pk=settings.CURRENT_META_COMPETITION_ID)
        for p in predictions:
            score = p.calculateScore()            
            p.calculateGoalDiff()
            p.needs_update = False
            p.save()
            if p.included_in_meta_competition == False:
                print p.competition.competition_date, now
            if p.included_in_meta_competition == False\
                   and p.competition.competition_date < now:
                running_score, _ = models.RunningScore.objects\
                                   .get_or_create(user=p.user,
                                                  competition=meta_competition)
                running_score.calculateScore(
                    new_score=p.score)
                running_score.calculateGoalDiff(
                    new_goaldiff=p.goaldiff)
                p.included_in_meta_competition = True
                p.save()                
            count += 1
        date = datetime.date.today()
        current = models.getCurrentTable()
        for comp in models.Competition.objects\
                .filter(competition_date__gt=yesterday):
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
                position = 1
                running_scores = comp.runningscore_set.all()
                for score in running_scores:
                    pos, created = models.Position.objects\
                                   .get_or_create(position=position,
                                                  date=date)
                    score.positions.add(pos)
                    if score.abs_change_on_last_position > 0:
                        position_changed.send(sender=None,
                                              prediction=score)
                    score.needs_ordering = False
                    score.save()
                    position += 1
            

        if count:
            print "Calculated %d scores in %f seconds" % (count, time.time() - start)
            print "(%f per second)" % (count/(time.time()-start))
