#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""This module is used to test GitHubCity class

Author: Israel Blancas @iblancasa
License:

The MIT License (MIT)
    Copyright (c) 2015 Israel Blancas @iblancasa (http://iblancasa.com/)

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software
    and associated documentation files (the “Software”), to deal in the Software without
    restriction, including without limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom
    the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or
    substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
    PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.

"""

import nose
from nose import tools
from nose.tools import eq_, ok_, assert_raises
import coloredlogs
import sys
import os
import datetime
import json
sys.path.append(os.getcwd()+"/githubcity")
from ghcity import *

###########################################################
# Gobal variables
###########################################################
idGH = None
secretGH = None
city = None
url = None
config = None


def setup():
    global config
    config = {
        "excludedLocations": [
            "Granada"
        ],
        "excludedUsers": [
            "vrivas"
        ],
        "intervals": [
            [
                "2008-01-01",
                "2015-12-24"
            ]
        ],
        "last_date": "2015-12-24",
        "locations": [
            "Jaén"
        ],
        "name": "Jaen"
    }

def test_githubKeys():
    """GitHub keys are inserted correctly
    """
    global idGH, secretGH

    idGH = os.environ.get('GH_ID')
    ok_(idGH!=None, "GitHub ID is None")
    ok_(idGH!="", "GitHub ID is an empty str")

    secretGH = os.environ.get('GH_SECRET')
    ok_(secretGH!=None, "GitHub Secret is None")
    ok_(secretGH!="", "GitHub ID is an empty str")



def test_classCreation():
    """GitHubCity instance is created correctly
    """
    global idGH, secretGH, city, config

    assert_raises(Exception,GitHubCity, None, None)
    assert_raises(Exception,GitHubCity, "asdad78asdd48ad4",None)
    assert_raises(Exception,GitHubCity, None, "asdad78asdd48ad4")

    city = GitHubCity(idGH, secretGH, config=config)
    ok_(city._intervals!=None, "City was not created correctly from config")

    city = GitHubCity(idGH, secretGH, config=None,locations=["Granada"], city="Granada",
        excludedUsers=["iblancasa"], excludedLocations=["Europe"], debug=True)
    ok_(city._city!=None, "City was not created correctly")
    coloredlogs.install(level='CRITICAL')

def test_loadConfiguration():
    """Loading configuration from file
    """
    city = GitHubCity(idGH, secretGH)
    city.readConfigFromJSON("testConfig.json")
    ok_(city._city=="Jaen", "Configuration was not load correctly from JSON")


def test_urlComposition():
    """URL's are composed correctly
    """
    global url, city
    url = city._getURL()

    expected_url = "https://api.github.com/search/users?client_id="+\
    city._githubID + "&client_secret=" + city._githubSecret +\
    "&order=desc&q=sort:joined+type:user+location:" + city._city + "&sort=joined&order=asc&per_page=100&page=1"

    eq_(url, expected_url, "URL is not well formed when there are not params " + url)

    url = city._getURL(2)
    expected_url = "https://api.github.com/search/users?client_id="+\
    city._githubID + "&client_secret=" + city._githubSecret +\
    "&order=desc&q=sort:joined+type:user+location:" + city._city + "&sort=joined&order=asc&per_page=100&page=2"

    eq_(url, expected_url, "URL is not well formed when there are 1 param (page) " + url)


    expected_url = "https://api.github.com/search/users?client_id="+\
        city._githubID + "&client_secret=" + city._githubSecret +\
        "&order=desc&q=sort:joined+type:user+location:"+ city._city +"+created:2008-01-01..2015-12-18"+\
        "&sort=joined&order=asc&per_page=100&page=2"
    url = city._getURL(2,"2008-01-01", "2015-12-18")
    eq_(url, expected_url, "URL is not well formed when there are 3 params (page and dates) " + url)


    expected_url = "https://api.github.com/search/users?client_id="+\
        city._githubID + "&client_secret=" + city._githubSecret +\
        "&order=desc&q=sort:joined+type:user+location:"+ city._city +"+created:2008-01-01..2015-12-18"+\
        "&sort=joined&order=desc&per_page=100&page=2"
    url = city._getURL(2,"2008-01-01", "2015-12-18","desc")
    eq_(url, expected_url, "URL is not well formed when there are 4 params (page, dates and sort) " + url)



def test_readAPI():
    """Reading API"""
    global city, url, data

    data = city._readAPI(url)
    ok_(data!=None, "Data received from API is None")
    ok_("total_count" in data, "Total_count is not correct")
    ok_("items" in data, "Items are not correct")


def test_addUser():
    """Add new users to the list"""
    global city

    city._addUser("nitehack")
    eq_(len(city._myusers), 1, "User was not added to the names list")
    eq_(len(city._dataUsers), 1, "User was not added to the dataUsers list")

    city._addUser("nitehack")
    eq_(len(city._myusers), 1, "User was added two times to the names list")
    eq_(len(city._dataUsers), 1, "User was added two times to the dataUsers list")

    ok_("nitehack" in city._myusers,
                  "Add new user was no completed correctly when there is an excluded list")

    city._addUser("iblancasa")
    ok_(not "iblancasa" in city._myusers,
                     "User was added to the users list and he is in excluded list")

    city._addUser("JJ")

    for i in city._dataUsers:
        ok_(i.getName() !="JJ", "User was added to the list when his location was excluded")


def test_getBestIntervals():
    """Get best intervals to query"""
    global city
    city = GitHubCity(idGH, secretGH,city="Barcelona", debug=True)
    city.calculateBestIntervals()

    for i in city._intervals:
        ok_(i[0]!="" and i[0]!=None, "First part of interval is not correct")


def test_strCity():
    """Checking if str is correct
    """
    global city
    ok_(isinstance(str(city),str), "Str of city is not correct")


def test_getAllUsers():
    """Get all users from a city
    """
    global idGH, secretGH, city
    city.getCityUsers()
    ok_(len(city._myusers)>=len(city._dataUsers), "Get all users is not ok")

    smallCity = GitHubCity(idGH, secretGH, config=None,locations=["Ceuta"], city="Ceuta",
    excludedUsers=[], excludedLocations=[], debug=True)
    smallCity.getCityUsers()
    ok_(len(smallCity._myusers)>=len(smallCity._dataUsers), "Get all users without calcule intervals\
        before is correct")


def test_getTotalUsers():
    """Total users number is correct
    """
    global city

    users = city.getTotalUsers()
    eq_(users,len(city._dataUsers), "Get users is not correct when there are users")


def test_getSortUsers():
    """Getting sort users
    """
    global city
    users = city.getSortedUsers("name")
    ok_(users[0].getName() >= users[1].getName(), "Users are not sorted correctly -name")
    users = city.getSortedUsers("lstreak")
    ok_(users[0].getLongestStreak() >= users[1].getLongestStreak(), "Users are not sorted correctly -lstreak")
    users = city.getSortedUsers("cstreak")
    ok_(users[0].getCurrentStreak() >= users[1].getCurrentStreak(), "Users are not sorted correctly -cstreak")
    users = city.getSortedUsers("language")
    ok_(users[0].getLanguage() >= users[1].getLanguage(), "Users are not sorted correctly -language")
    users = city.getSortedUsers("followers")
    ok_(users[0].getFollowers() >= users[1].getFollowers(), "Users are not sorted correctly -followers")
    users = city.getSortedUsers("join")
    ok_(users[0].getJoin() >= users[1].getJoin(), "Users are not sorted correctly -join")
    users = city.getSortedUsers("organizations")
    ok_(users[0].getOrganizations() >= users[1].getOrganizations(), "Users are not sorted correctly -organizations")
    users = city.getSortedUsers("repositories")
    ok_(users[0].getNumberOfRepositories() >= users[1].getNumberOfRepositories(), "Users are not sorted correctly -repositories")
    users = city.getSortedUsers("stars")
    ok_(users[0].getStars() >= users[1].getStars(), "Users are not sorted correctly -stars")
    users = city.getSortedUsers("contributions")
    ok_(users[0].getContributions() >= users[1].getContributions(), "Users are not sorted correctly -contributions")


def test_export():
    """Exporting users"""
    global city
    city.export("testTemplate", "out", "contributions")


def test_getConfig():
    city = GitHubCity(idGH, secretGH)
    city.readConfigFromJSON("testConfig.json")
    city.configToJson("asd.json")
    city2 = GitHubCity(idGH, secretGH)
    city2.readConfigFromJSON("asd.json")
    eq_(city._city,city2._city, "Configuration was not saved correctly")


def test_checkWhenApiLimit():
    """Checking when the API limit is reached
    """
    global url, city
    i = 0
    while i<50:
        result = city._readAPI(url)
        i+=1

    ok_(result!=None, "Problem checking when API limit is reached")
