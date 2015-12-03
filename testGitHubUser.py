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
from GitHubUser import *
import datetime

###########################################################
# Gobal variables
###########################################################
user = None

def setup():
    pass

def test_classCreation():
    """Class is created correctly"""
    global user
    user = GitHubUser("iblancasa")
    eq_(user._name,"iblancasa", "Class was not created correctly")

def testGettingData():
    """Get data is correct"""
    global user
    user.getData()
    ok_(user._contributions!=None,"Contributions is not correctly")
    ok_(user._longestStreak!=None,"Longest streak is not correctly")
    ok_(user._currentStreak!=None,"Current streak is not correctly")
    ok_(user._language!=None,"Language is not correctly")
    ok_(user._avatar!=None,"Avatar is not correctly")
    ok_(user._followers!=None,"Followers is not correctly")
    ok_(user._location!=None,"Location is not correctly")
    ok_(user._join!=None,"Join is not correctly")
    ok_(user._organizations!=None,"Organizations is not correctly")
    ok_(user._numRepos!=None,"numRepos is not correctly")
    ok_(user._stars!=None,"Stars is not correctly")

def testGetters():
    """Testing getters"""
    global user
    eq_(user._name, user.getName(),"Name getter is not correctly")
    eq_(user._contributions, user.getContributions(),"Contributions getter is not correctly")
    eq_(user._longestStreak, user.getLongestStreak(),"Longest getter streak is not correctly")
    eq_(user._currentStreak, user.getCurrentStreak(),"Current getter streak is not correctly")
    eq_(user._language, user.getLanguage(),"Language getter is not correctly")
    eq_(user._avatar, user.getAvatar(),"Avatar getter is not correctly")
    eq_(user._followers, user.getFollowers(),"Followers getter is not correctly")
    eq_(user._location, user.getLocation(),"Location getter is not correctly")
    eq_(user._join, user.getJoin(),"Join getter is not correctly")
    eq_(user._organizations, user.getOrganizations(),"Organizations getter is not correctly")
    eq_(user._numRepos, user.getNumberOfRepositories(),"numRepos getter is not correctly")
    eq_(user._stars, user.getStars(),"Stars getter is not correctly")

def testLotOfRequest():
    global user
    i = 0
    print(datetime.datetime.now().time())
    while i<50:
        user._contributions = 0
        user.getData()
        i+=1
    print(datetime.datetime.now().time())
    ok_(user._contributions!=0, "Lot of request fail")
