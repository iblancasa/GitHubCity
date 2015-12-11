#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module allow to developers to get all some data about a given GitHub user.

Author: Israel Blancas @iblancasa
Original idea: https://github.com/JJ/github-city-rankings
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
import time
from bs4 import BeautifulSoup
import urllib.request
from urllib.error import HTTPError, URLError
import datetime, dateutil.parser
import re

class GitHubUser:
    """Manager of a GitHub User

    Attributes:
        _name (str): Name of the user (private).
        _contributions (int): total contributions of a user in the last year (private).
        _followers (int): total number of followers of an user (private).
        _gists (int): total number of gists of an user (private).
        _longestStreak (int): maximum number of consecutive days with activity (private).
        _numRepos (int): number of repositories of an user (private).
    """

    def __init__(self, name):
        """Constructor of the class.
        Args:
            name (str): name (login) of an user in GitHub

        Returns:
            a new instance of GitHubUser class
        """
        self._name = name

    def getName(self):
        return self._name

    def getContributions(self):
        return self._contributions

    def getLongestStreak(self):
        return self._longestStreak

    def getCurrentStreak(self):
        return self._currentStreak

    def getLanguage(self):
        return self._language

    def getAvatar(self):
        return self._avatar

    def getFollowers(self):
        return self._followers

    def getLocation(self):
        return self._location

    def getJoin(self):
        return self._join

    def getOrganizations(self):
        return self._organizations

    def getNumberOfRepositories(self):
        return self._numRepos

    def getStars(self):
        return self._stars


    def getData(self):
        """Get data of a GitHub user.
        """

        url = "https://github.com/"+self._name

        data = self._getDataFromURL(url)
        web = BeautifulSoup(data,"lxml")

        #Contributions, longest streak and current streak
        contributions_raw = web.find_all('span',{'class':'contrib-number'})
        self._contributions = int(contributions_raw[0].text.split(" ")[0].replace(",",""))
        self._longestStreak = int(contributions_raw[1].text.split(" ")[0].replace(",",""))
        self._currentStreak = int(contributions_raw[2].text.split(" ")[0].replace(",",""))

        #Language
        self._language = web.find("meta", {"name":"description"})['content'].split(" ")[6]
        if self._language[len(self._language)-1]==",":
            self._language = self._language[:-1]

        #Avatar
        self._avatar = web.find("img", {"class":"avatar"})['src'][:-10]

        #Followers
        vcard = web.find_all("strong", {"class":"vcard-stat-count"})
        self._followers = int(vcard[0].text)

        #Location
        self._location = web.find("li", {"itemprop":"homeLocation"}).text

        #Date of creation
        self._join = dateutil.parser.parse(web.find("time",{"class":"join-date"})["datetime"])

        #Number of organizations
        self._organizations = len(web.find_all("a",{"class":"avatar-group-item"}))

        #Number of repos
        url +="?tab=repositories"
        data = self._getDataFromURL(url)
        web = BeautifulSoup(data,"lxml")

        repos = web.find_all("a",{"aria-label":"Stargazers"})
        self._numRepos = (len(repos))

        #Number of total stars
        stars = 0
        non_decimal = re.compile(r'[^\d]+')

        for repo in repos:
            stars += int(non_decimal.sub('', repo.text))

        self._stars = stars

    def _getDataFromURL(self, url):
        code = 0

        hdr = {'User-Agent': 'curl/7.43.0 (x86_64-ubuntu) libcurl/7.43.0 OpenSSL/1.0.1k zlib/1.2.8 gh-rankings-grx',
               'Accept': 'text/html'
               }

        while code != 200:
            req = urllib.request.Request(url, headers=hdr)
            try:
                response = urllib.request.urlopen(req)
                code = response.code
            except HTTPError as e:
                time.sleep(5)
                code = e.code
            except URLError as e:
                time.sleep(5)
                code = 0
        return response.read().decode('utf-8')
