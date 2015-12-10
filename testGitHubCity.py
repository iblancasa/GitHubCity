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

import sys
import os
import json
sys.path.append(os.getcwd())
from GitHubCity import *

###########################################################
# Gobal variables
###########################################################
idGH = None
secretGH = None

cityA = None
cityB = None
cityC = None

data = None
url = None
dataExclude = None
excluded = None

def setup():
    global dataExclude, excluded
    dataExclude = [
        {
            "login": "iblancasa",
            "id": 99999,
            "avatar_url": "https://avatars.githubusercontent.com/u/99999?v=3",
            "gravatar_id": "",
            "url": "https://api.github.com/users/asdpokjdf",
            "html_url": "https://github.com/asdpokjdf",
            "followers_url": "https://api.github.com/users/asdpokjdf/followers",
            "following_url": "https://api.github.com/users/asdpokjdf/following{/other_user}",
            "gists_url": "https://api.github.com/users/asdpokjdf/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/asdpokjdf/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/asdpokjdf/subscriptions",
            "organizations_url": "https://api.github.com/users/asdpokjdf/orgs",
            "repos_url": "https://api.github.com/users/asdpokjdf/repos",
            "events_url": "https://api.github.com/users/asdpokjdf/events{/privacy}",
            "received_events_url": "https://api.github.com/users/asdpokjdf/received_events",
            "type": "User",
            "site_admin": "false",
            "score": 1.0
        },
        {
            "login": "nitehack",
            "id": 99999,
            "avatar_url": "https://avatars.githubusercontent.com/u/99999?v=3",
            "gravatar_id": "",
            "url": "https://api.github.com/users/asdpokjdf",
            "html_url": "https://github.com/asdpokjdf",
            "followers_url": "https://api.github.com/users/asdpokjdf/followers",
            "following_url": "https://api.github.com/users/asdpokjdf/following{/other_user}",
            "gists_url": "https://api.github.com/users/asdpokjdf/gists{/gist_id}",
            "starred_url": "https://api.github.com/users/asdpokjdf/starred{/owner}{/repo}",
            "subscriptions_url": "https://api.github.com/users/asdpokjdf/subscriptions",
            "organizations_url": "https://api.github.com/users/asdpokjdf/orgs",
            "repos_url": "https://api.github.com/users/asdpokjdf/repos",
            "events_url": "https://api.github.com/users/asdpokjdf/events{/privacy}",
            "received_events_url": "https://api.github.com/users/asdpokjdf/received_events",
            "type": "User",
            "site_admin": "false",
            "score": 1.0
        }
        ]

    fileJSON = open('testExclude.json')
    excluded = json.loads(fileJSON.read())
    fileJSON.close()



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
    global idGH, secretGH, cityA

    assert_raises(Exception,GitHubCity, None, None, None)
    assert_raises(Exception,GitHubCity,"Granada", None, None)
    assert_raises(Exception,GitHubCity,"Granada", "asdad78asdd48ad4", None)

    cityA = GitHubCity("Granada", idGH, secretGH)
    ok_(cityA!=None, "City was not created")
    ok_(cityA._city!=None, "City name was not setting")
    ok_(cityA._githubID!=None, "GitHub ID was not setting")
    ok_(cityA._githubSecret!=None, "GitHub Secret was not setting")
    eq_(cityA._githubID, os.environ.get('GH_ID'), "GitHub ID was not setting correctly")
    eq_(cityA._githubSecret, os.environ.get('GH_SECRET'), "GitHub Secret was not setting correctly")
    ok_(cityA._city!="", "City name is an empy str")



def test_periodCalculation():
    """Period is calculated correctly
    """
    global cityA, start,finish
    start = datetime.date(2015, 2, 1)
    finish = datetime.date(2015, 1, 1)
    start_result, final_result = cityA._getPeriod(start, finish)
    difference_dates = start_result - final_result
    difference_dates2 = start - start_result

    eq_(difference_dates.days, 31, "Diference between " + str(final_result) + " and " +
                     str(start_result) + " is incorrect")
    eq_(difference_dates2.days, 32, "Diference between " + str(start_result) + " and " +
                     str(start) + " is incorrect")
    eq_(start_result + relativedelta(days=+1), finish ,
                     "Finish date and start result \ date must be differenced in one day")



def test_urlComposition():
    """URL's are composed correctly
    """
    global url, cityA, start, finish

    url = cityA._getURL(1, finish, start)
    expected_url = "https://api.github.com/search/users?client_id=" +\
        cityA._githubID + "&client_secret=" + cityA._githubSecret + "&order=desc&q=sort:joined+" +\
        "type:user+location:Granada+created:2015-01-01..2015-02-01&per_page=100&page=1"

    ok_(url!=None, "URL was not returned")
    ok_(url!="", "URL is an empty string")
    eq_(url, expected_url, "URL is not well formed"+str(start)+" "+str(finish)+" "+url)



def test_readAPI():
    """Reading API"""
    global cityA, url, data

    data = cityA._readAPI(url)
    ok_(data!=None, "Data received from API is None")
    eq_(data["total_count"], 16, "Total_count is not correct")
    eq_(len(data["items"]), 16, "Items are not correct")


def test_addUser():
    """Add new users to the list"""
    global idGH, secretGH, cityA, start, finish, cityB

    added = cityA._addUsers(data["items"])
    ok_(cityA._names!=None, "Users in class is None")
    eq_(len(cityA._names), data["total_count"], "Users were not saved correctly")
    eq_(added, data["total_count"], "The number of users added is not correct")

    added = cityA._addUsers(data["items"])
    eq_(added, 0, "The number of users added when all users are repeated is not correct")

    cityB = GitHubCity("Granada", idGH, secretGH)
    cityB._getPeriodUsers(finish, start)
    eq_(cityA._names, cityB._names, "Get period (short) is not OK")


def test_getAllUsers():
    """Get all users from a city
    """
    global idGH, secretGH, cityC

    cityC = GitHubCity("Granada", idGH, secretGH)
    url_all = "https://api.github.com/search/users?client_id=" + \
        idGH + "&client_secret=" + secretGH + \
        "&q=type:user+location:Granada"

    data_all = cityC._readAPI(url_all)
    cityC.getCityUsers()
    eq_(len(cityC._names), data_all[
                     "total_count"], "Total users was not calculated correctly")



def test_excludeUsers():
    """Excluded users that are excluded from the list
    """
    global idGH, secretGH, excluded, dataExclude

    cityD = GitHubCity("Granada", idGH, secretGH, excluded)
    cityD._addUsers(dataExclude)

    ok_("nitehack" in cityD._names,
                  "Add new user was no completed correctly when there is an excluded list")
    ok_(not "iblancasa" in cityD._names,
                     "User was added to the users list and he is in excluded list")



def test_getTotalUsers():
    """Total users number is correct
    """
    global cityC

    users = cityC.getTotalUsers()
    eq_(users,len(cityC._names), "Get users is not correct when there are users")

    city = GitHubCity("Test","asdad","asdasd")
    eq_(city.getTotalUsers(),-1, "Get users is not correct when there are not users")
