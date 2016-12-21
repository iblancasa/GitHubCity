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
from nose.tools import *

import sys
import os
import json
import datetime
import httpretty
sys.path.append(os.getcwd()+"/githubcity")
from ghuser import *
from ghcity import *


files = {}

idGH = ""
secretGH = ""

def setup():
    global files
    global idGH
    global secretGH

    idGH = os.environ.get('GH_ID')
    secretGH = os.environ.get('GH_SECRET')

    with open("tests/user.txt", 'r') as content_file:
        files['user'] = content_file.read()


@httpretty.activate
def testGettingData():
    """Get data is correct"""
    httpretty.register_uri(httpretty.GET, "https://github.com/iblancasa",
                           body=files['user'])

    user = GitHubUser("iblancasa")

    user.getData()

    ok_(user._followers!=-1,"Followers is not correct")
    ok_(user._numRepos!=-1,"The number of the repositories is not correct")
    ok_(user._organizations!=-1,"Organizations is not correct")
    ok_(user._contributions!=-1,"Contributions is not correct")
    ok_(user._join!="","Join is not correct")
    ok_(user._avatar!="","Avatar is not correct")
    ok_(user._bio!="","Bio is not correct")
    ok_(user._avatar!="","Avatar is not correct")


def testExport():
    """Test export"""
    httpretty.register_uri(httpretty.GET, "https://github.com/iblancasa",
                           body=files['user'])

    user = GitHubUser("iblancasa")

    user.getData()
    data = user.export()

    ok_("name" in data, "Export is correct")


def test_urlComposition():
    """URL's are composed correctly
    """
    city = GitHubCity(idGH, secretGH, config=None,locations=["Granada"], city="Granada", excludedUsers=["iblancasa"], excludedLocations=["Europe"])


    url = city._getURL()

    expected_url = "https://api.github.com/search/users?client_id="+\
    city._githubID + "&client_secret=" + city._githubSecret +\
    "&order=desc&q=sort:joined+type:user+location:\"" + city._city + "\"&sort=joined&order=asc&per_page=100&page=1"
    eq_(url, expected_url, "URL is not well formed when there are not params " + url)

    url = city._getURL(2)
    expected_url = "https://api.github.com/search/users?client_id="+\
    city._githubID + "&client_secret=" + city._githubSecret +\
    "&order=desc&q=sort:joined+type:user+location:\"" + city._city + "\"&sort=joined&order=asc&per_page=100&page=2"

    eq_(url, expected_url, "URL is not well formed when there are 1 param (page) " + url)


    expected_url = "https://api.github.com/search/users?client_id="+\
        city._githubID + "&client_secret=" + city._githubSecret +\
        "&order=desc&q=sort:joined+type:user+location:\""+ city._city +"\"+created:2008-01-01..2015-12-18"+\
        "&sort=joined&order=asc&per_page=100&page=2"
    url = city._getURL(2,"2008-01-01", "2015-12-18")
    eq_(url, expected_url, "URL is not well formed when there are 3 params (page and dates) " + url)


    expected_url = "https://api.github.com/search/users?client_id="+\
        city._githubID + "&client_secret=" + city._githubSecret +\
        "&order=desc&q=sort:joined+type:user+location:\""+ city._city +"\"+created:2008-01-01..2015-12-18"+\
        "&sort=joined&order=desc&per_page=100&page=2"
    url = city._getURL(2,"2008-01-01", "2015-12-18","desc")
    eq_(url, expected_url, "URL is not well formed when there are 4 params (page, dates and sort) " + url)
