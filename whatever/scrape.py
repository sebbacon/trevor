# coding=utf-8

import urllib2
from BeautifulSoup import BeautifulSoup
#import settings
from datetime import timedelta

import settings

LAST_YEAR_FAKE = [u'Manchester United', u'Liverpool', u'Chelsea', u'Arsenal', u'Everton', u'Aston Villa', u'Fulham', u'Tottenham Hotspur', u'West Ham United', u'Manchester City', u'Wigan Athletic', u'Stoke City', u'Bolton Wanderers', u'Portsmouth', u'Blackburn Rovers', u'Sunderland', u'Hull City', u'Newcastle United', u'Middlesbrough', u'West Bromwich Albion']

THIS_YEAR_FAKE = [u'Chelsea', u'Tottenham Hotspur', u'Manchester United', u'Manchester City', u'Stoke City', u'Arsenal', u'Liverpool', u'Aston Villa', u'Sunderland', u'Burnley', u'West Ham United', u'Birmingham City', u'Wolverhampton Wanderers', u'Hull City', u'Fulham', u'Everton', u'Wigan Athletic', u'Blackburn Rovers', u'Bolton Wanderers', u'Portsmouth']


URL_TEMPLATE = "http://en.wikipedia.org/wiki/%s–%s_Premier_League?a=2"

def parseTable(year):
    if settings.OFFLINE:
        return fakeTable(year)
    else:
        next_year = year + timedelta(366)
        url = URL_TEMPLATE % (year.strftime("%Y"),
                              next_year.strftime("%y"))
        request = urllib2.Request(url)
        request.add_header("User-Agent",
                           "WhateverTrevor/0.1 +http://whatevertrevor.com")

        opener = urllib2.build_opener()
        page = opener.open(request).read() 
        soup = BeautifulSoup(page)
        anchor = soup.find(True, {"id":"League_table"})
        table = anchor.findAllNext("table")
        teams = []
        for row in table[0].findAll("tr")[1:]:
            cells = row.findAll("td")
            position, team = cells[0].string, cells[1].a.string
            teams.append(team.title())
        return teams


def parsePremierTeams():
    url = URL_TEMPLATE % ("2010", "11")
    request = urllib2.Request(url)
    request.add_header("User-Agent",
                       "WhateverTrevor/0.1 +http://whatevertrevor.com")

    opener = urllib2.build_opener()
    page = opener.open(request).read() 
    soup = BeautifulSoup(page)
    anchor = soup.find(True, {"id":"League_table"})
    table = anchor.findAllNext("table")
    teams = []
    for row in table[0].findAll("tr")[1:]:
        cells = row.findAll("td")
        position, team = cells[0].string, cells[1].a.string
        teams.append(team.title())
    return teams
    
def parseChampionship():

    tid = "History_of_the_current_24_clubs_in_the_Championship_.282010.E2.80.9311_season.29"    
    url = "http://en.wikipedia.org/wiki/Football_League_Championship"
    request = urllib2.Request(url)
    request.add_header("User-Agent",
                       "WhateverTrevor/0.1 +http://whatevertrevor.com")

    opener = urllib2.build_opener()
    page = opener.open(request).read() 
    soup = BeautifulSoup(page)
    anchor = soup.find(True, {"id":tid})
    table = anchor.findAllNext("table")
    teams = []
    for row in table[0].findAll("tr")[1:]:
        cells = row.findAll("td")
        team = cells[0].findAll("a")[0].string
        teams.append(team)
    return teams
    
def parseLeagueOne():
    url = "http://en.wikipedia.org/wiki/Football_League_One"
    request = urllib2.Request(url)
    request.add_header("User-Agent",
                       "WhateverTrevor/0.1 +http://whatevertrevor.com")

    opener = urllib2.build_opener()
    page = opener.open(request).read() 
    soup = BeautifulSoup(page)
    anchor = soup.find(True, {"id":"Football_League_One_clubs_2009.E2.80.9310"})
    table = anchor.findAllNext("table")
    teams = []
    for row in table[0].findAll("tr")[1:]:
        cells = row.findAll("td")
        team = cells[0].findAll("a")[0].string
        teams.append(team)
    return teams
    
def parseLeagueTwo():
    url = "http://en.wikipedia.org/wiki/Football_League_Two"
    request = urllib2.Request(url)
    request.add_header("User-Agent",
                       "WhateverTrevor/0.1 +http://whatevertrevor.com")

    opener = urllib2.build_opener()
    page = opener.open(request).read() 
    soup = BeautifulSoup(page)
    anchor = soup.find(True, {"id":"Football_League_Two_clubs_2009.E2.80.9310"})
    table = anchor.findAllNext("table")
    teams = []
    for row in table[0].findAll("tr")[1:]:
        cells = row.findAll("td")
        team = cells[0].findAll("a")[0].string
        teams.append(team)
    return teams

def parseConference():
    url = "http://en.wikipedia.org/wiki/Conference_National"
    request = urllib2.Request(url)
    request.add_header("User-Agent",
                       "WhateverTrevor/0.1 +http://whatevertrevor.com")

    opener = urllib2.build_opener()
    page = opener.open(request).read() 
    soup = BeautifulSoup(page)
    anchor = soup.find(True, {"id":"Conference_National_clubs_2009-10"})
    table = anchor.findAllNext("table")
    teams = []
    for row in table[0].findAll("tr")[1:]:
        cells = row.findAll("td")
        team = cells[0].findAll("a")[0].string
        teams.append(team)
    return teams

def fakeTable(year):
    if int(year.strftime("%Y")) == settings.CURRENT_SEASON:
        return THIS_YEAR_FAKE
    else:
        return LAST_YEAR_FAKE

if __name__ == "__main__":
    print parseConference()
