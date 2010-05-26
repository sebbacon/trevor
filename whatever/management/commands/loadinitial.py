from django.core.management.base import BaseCommand, CommandError

from whatever.models import CustomUser, Team, Prediction
import utils

import csv
import os

INITIAL_TABLE = ["Arsenal", "Aston Villa", "Birmingham City",
                 "Blackburn Rovers","Bolton Wanderers",
                 "Burnley", "Chelsea", "Everton",
                 "Fulham", "Hull City", "Liverpool",
                 "Manchester City", "Manchester United",
                 "Portsmouth", "Stoke City", "Sunderland",
                 "Tottenham Hotspur", "West Ham United",
                 "Wigan Athletic", "Wolverhampton Wanderers"]

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not args:
            raise CommandError("USAGE: ./manage.py %s <csvfile>" % \
                    os.path.basename(__file__).split('.')[0])
        this_year = utils.getThisYear()
        csvfile = open(args[0])
        dialect = csv.Sniffer().sniff(csvfile.read(1024))
        csvfile.seek(0)
        users = csv.DictReader(csvfile, dialect=dialect)
        seen = []
        for user in users:
            email = user["userEmail_str"]
            if email in seen:
                continue
            order = user["userOrder_str"]
            order = order.split(",")
            positions = [Team.objects.get(name=INITIAL_TABLE[int(o)-1])\
                         for o in order]
            user = CustomUser.objects.create(username=email,
                                             email=email,
                                             postcode="",
                                             can_email=False,
                                             password="password",
                                             first_name="",
                                             last_name="",
                                             is_active=True)
            user.save()
            prediction_obj = Prediction(name=email,
                                        year=this_year,
                                        user=user)
            prediction_obj.save()
            for p in positions:
                prediction_obj.teams.add(p)
            prediction_obj.save()
            seen.append(email)
            print prediction_obj
