import urllib2
from datetime import datetime
from datetime import timedelta
from sets import Set
import sys

fixtureurl = "http://api.scraperwiki.com/api/1.0/datastore/getdata?key=e1599319b01d876281589c630ca87826&format=json&name=upcoming-premiership-fixtures"
teamurl = "http://api.scraperwiki.com/api/1.0/datastore/getdata?key=e1599319b01d876281589c630ca87826&format=json&name=premier-league-table"

def get_data():
    request = urllib2.Request(teamurl)
    request.add_header("User-Agent",
                       "WhateverTrevor/0.1 +http://whatevertrevor.com")

    opener = urllib2.build_opener()
    teams = eval(opener.open(request).read())

    request = urllib2.Request(fixtureurl)
    request.add_header("User-Agent",
                       "WhateverTrevor/0.1 +http://whatevertrevor.com")

    opener = urllib2.build_opener()
    fixtures = eval(opener.open(request).read())

    return teams, fixtures

class Unbuffered:  
     def __init__(self, stream):
         self.stream = stream
     def write(self, data):
         self.stream.write(data)
         self.stream.flush()
     def __getattr__(self, attr):
         return getattr(self.stream, attr)
     
def ncycle(seq,n):
    while True:
        for x in seq:
            for dummy in xrange(n):
                yield x

def cross(*args):
    p,R = 1,[]
    for arg in args:
        L = list(arg)
        R.append(ncycle(L,p))
        p *= len(L)
    #R.reverse()
    for dummy in xrange(p):
        yield tuple(x.next() for x in R)

def real():
    for x in cross((0,1), (0,1),(0,1),(0,1)):
        print x



CHOICES = "WLD"
def outcomes(fixtures, poss=None):
    if not poss:
        poss = []
    try:
        fixture = fixtures.pop()
        home, away = fixture
        for choice in CHOICES:
            poss.append((home, choice, away))
            poss = outcomes(fixtures, poss)
    except IndexError:
        pass                
    return poss
            


def examine_outcomes(start_date, end_date):
    teams, fixtures = get_data()
    table_data = {}
    for team in teams:
        table_data[team['team']] = int(team['pts'])
    matches = []
    for fixture in fixtures:
        date = datetime.strptime(fixture['date'],"%Y-%m-%d %H:%M:00")
        if start_date < date < end_date:
            matches.append((fixture['home'], fixture['away']))

    ordered_tables = Set()
    
    examined = 0
    print "examining", len(matches), "matches"
    print matches
    match_num = len(matches)
    sys.stdout = Unbuffered(sys.stdout)
    examined = 0
    step = 0
    for home, outcome, away in outcomes(matches):
        print home, outcome, away

def frob():
    
    for outcome_map in cross(*[(0,1)]*(match_num*2)):
        #print "**** outcomes:", outcome_map
        outcome_map = iter(outcome_map)
        idx = 0
        this_table = table_data.copy()
        for home in outcome_map:
            away = outcome_map.next()
            hometeam = matches[idx][0]
            awayteam = matches[idx][1]
            if home == away:
                this_table[hometeam] += 1
                this_table[awayteam] += 1
                #print hometeam, "and", awayteam, "draw ;",
            elif home > away:
                this_table[hometeam] += 3
                #print hometeam, "beats", awayteam, ";"
            elif away > home:
                this_table[awayteam] += 3
                #print awayteam, "beats", hometeam, ";"
            idx += 1
        examined += 1
        step += 1
        if step % 500000 == 0:
            print examined
        #sys.stdout.write("*")
        ordered = this_table.items()
        ordered.sort(lambda x, y: cmp(y[1], x[1]))
        ordered_tables.add(tuple([x[0] for x in ordered]))
        #print len(ordered_tables), examined
    print "%d possible tables from %d outcomes" % \
          (len(ordered_tables), examined)
    #for table in ordered_tables:
    #    for team in table:
    #        print team
    #    print "----"
        

now = datetime.now()
for days in range(1,8):
    print "in", days, "days",
    examine_outcomes(now,
                     now + timedelta(days))
    print
