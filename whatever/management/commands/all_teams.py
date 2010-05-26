import os

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from whatever import models
from whatever import scrape

def getOrMakeTeam(name, league):
    
    league, created = models.Division.objects.get_or_create(name=str(league))
    team, created = models.Team.objects.get_or_create(name=str(name))
    team.division=league
    team.save()
    return team, league

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not args or (args and args[0] not in ('load')):
            raise CommandError("USAGE: ./manage.py %s load" % \
                    os.path.basename(__file__).split('.')[0])

        transaction.enter_transaction_management()
        transaction.managed(True)

        divisions = ['Premier League',
                     'Championship',
                     'League One',
                     'League Two',
                     'Conference']

        tables = {}
        tables['Premier League'] = scrape.parsePremierTeams()
        tables['Championship'] = scrape.parseChampionship()
        tables['League One'] = scrape.parseLeagueOne()
        tables['League Two'] = scrape.parseLeagueTwo()
        tables['Conference'] = scrape.parseConference()

        for division in divisions:
            for team in tables[division]:
                team, division = getOrMakeTeam(team, division)
                print "done", team, division
        
        transaction.commit()
