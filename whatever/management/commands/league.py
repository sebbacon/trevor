import os

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from whatever import models
from whatever import scrape
import settings
import utils

def getOrMakeTeam(name):
    try:
        team = models.Team.objects.get(name=name)
    except models.Team.DoesNotExist:
        team = models.Team(name=name)
        team.save()
    return team    

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not args or (args and args[0] not in ('load')):
            raise CommandError("USAGE: ./manage.py %s load" % \
                    os.path.basename(__file__).split('.')[0])

        transaction.enter_transaction_management()
        transaction.managed(True)
        this_year = utils.getThisYear()
        last_year = utils.getLastYear()
        table = scrape.parseTable(this_year)
        teams_table = []
        prev_current = models.getCurrentTable()
        for name in table:
            teams_table.append(getOrMakeTeam(name))
        current = models.LeagueTable(name=settings.CURRENT_LEAGUE_ID,
                                     year=this_year)
        current.save()
        for t in teams_table:            
            current.teams.add(t)
        current.save()
        if prev_current and list(current.ordered_teams) \
               == list(prev_current.ordered_teams):
            current.delete()
        else:
            print "table changed"
        if not models.getPreviousTable():
            previous = models.LeagueTable(name=settings.PREVIOUS_LEAGUE_ID,
                                          year=last_year)
            previous.save()
            for name in scrape.parseTable(last_year):
                previous.teams.add(getOrMakeTeam(name))
            previous.save()
            print previous
        transaction.commit()
