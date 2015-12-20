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
import json
sys.path.append(os.getcwd())
from GitHubCity import *

###########################################################
# Gobal variables
###########################################################
idGH = None
secretGH = None

cityA = None

url = None
excluded = None

def setup():
    global dataExclude, excluded
    os.environ['TZ'] = 'Europe/London'
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
    global idGH, secretGH

    assert_raises(Exception,GitHubCity, None, None, None)
    assert_raises(Exception,GitHubCity,"Granada", None, None)
    assert_raises(Exception,GitHubCity,"Granada", "asdad78asdd48ad4", None,debug=False)

    cityA = GitHubCity("Granada", idGH, secretGH, debug=True)
    ok_(cityA!=None, "City was not created")
    ok_(cityA._city!=None, "City name was not setting")
    ok_(cityA._githubID!=None, "GitHub ID was not setting")
    ok_(cityA._githubSecret!=None, "GitHub Secret was not setting")
    eq_(cityA._githubID, os.environ.get('GH_ID'), "GitHub ID was not setting correctly")
    eq_(cityA._githubSecret, os.environ.get('GH_SECRET'), "GitHub Secret was not setting correctly")
    ok_(cityA._city!="", "City name is an empy str")
    coloredlogs.install(level='CRITICAL')


def test_urlComposition():
    """URL's are composed correctly
    """
    global url, cityA
    cityA = GitHubCity("Granada", idGH, secretGH, debug=False)
    url = cityA._getURL()

    expected_url = "https://api.github.com/search/users?client_id="+\
    cityA._githubID + "&client_secret=" + cityA._githubSecret +\
    "&order=desc&q=sort:joined+type:user+location:" + cityA._city + "&sort=joined&order=asc&per_page=100&page=1"

    eq_(url, expected_url, "URL is not well formed when there are not params " + url)

    url = cityA._getURL(2)
    expected_url = "https://api.github.com/search/users?client_id="+\
    cityA._githubID + "&client_secret=" + cityA._githubSecret +\
    "&order=desc&q=sort:joined+type:user+location:" + cityA._city + "&sort=joined&order=asc&per_page=100&page=2"

    eq_(url, expected_url, "URL is not well formed when there are 1 param (page) " + url)


    expected_url = "https://api.github.com/search/users?client_id="+\
        cityA._githubID + "&client_secret=" + cityA._githubSecret +\
        "&order=desc&q=sort:joined+type:user+location:"+ cityA._city +"+created:2008-01-01..2015-12-18"+\
        "&sort=joined&order=asc&per_page=100&page=2"
    url = cityA._getURL(2,datetime.date(2008, 1, 1),datetime.date(2015, 12, 18))
    eq_(url, expected_url, "URL is not well formed when there are 3 params (page and dates) " + url)

    expected_url = "https://api.github.com/search/users?client_id="+\
        cityA._githubID + "&client_secret=" + cityA._githubSecret +\
        "&order=desc&q=sort:joined+type:user+location:"+ cityA._city +"+created:2008-01-01..2015-12-18"+\
        "&sort=joined&order=desc&per_page=100&page=2"
    url = cityA._getURL(2,datetime.date(2008, 1, 1),datetime.date(2015, 12, 18),"desc")
    eq_(url, expected_url, "URL is not well formed when there are 4 params (page, dates and sort) " + url)



def test_readAPI():
    """Reading API"""
    global cityA, url, data

    data = cityA._readAPI(url)
    ok_(data!=None, "Data received from API is None")
    ok_("total_count" in data, "Total_count is not correct")
    ok_("items" in data, "Items are not correct")


def test_addUser():
    """Add new users to the list"""
    global cityA

    cityA._addUser("iblancasa")
    eq_(len(cityA._myusers), 1, "User was not added to the names list")
    eq_(len(cityA._dataUsers), 1, "User was not added to the dataUsers list")

    cityA._addUser("iblancasa")
    eq_(len(cityA._myusers), 1, "User was added two times to the names list")
    eq_(len(cityA._dataUsers), 1, "User was added two times to the dataUsers list")


def test_getBestIntervals():
    """Get best intervals to query"""
    global cityA
    cityA = GitHubCity("Barcelona", idGH, secretGH, debug=True)
    cityA.calculateBestIntervals()

    for i in cityA._intervals:
        ok_(i[0]!="" and i[0]!=None, "First part of interval is not correct")
        ok_(i[1]!="" and i[0]!=None, "First part of interval is not correct")



def test_getAllUsers():
    """Get all users from a city
    """
    global cityA
    cityA.getCityUsers()
    ok_(len(cityA._myusers)>=len(cityA._dataUsers),"Get all users is not ok")


def test_excludeUsers():
    """Excluded users that are excluded from the list
    """
    global idGH, secretGH, excluded, dataExclude, cityA

    cityA = GitHubCity("Granada", idGH, secretGH, excluded)
    cityA._addUser("nitehack")
    cityA._addUser("iblancasa")

    ok_("nitehack" in cityA._myusers,
                  "Add new user was no completed correctly when there is an excluded list")
    ok_(not "iblancasa" in cityA._myusers,
                     "User was added to the users list and he is in excluded list")



def test_getTotalUsers():
    """Total users number is correct
    """
    global cityA

    users = cityA.getTotalUsers()
    eq_(users,len(cityA._dataUsers), "Get users is not correct when there are users")


def test_checkWhenApiLimit():
    """Checking when the API limit is reached
    """
    global url, cityA
    i = 0
    while i<50:
        result = cityA._readAPI(url)
        i+=1

    ok_(result!=None, "Problem checking when API limit is reached")
