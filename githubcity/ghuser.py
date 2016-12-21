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
from dateutil.relativedelta import relativedelta
import re

class GitHubUser:
    """Manager of a GitHub User

    Attributes:
        _name (str): Name of the user (private).
        _contributions (int): total contributions of an user in the last year (private).
        _public (int): public contributions of an user in the last year (private).
        _private (int): private contributions of an user in the last year (private).
        _followers (int): total number of followers of an user (private).
        _numRepos (int): number of repositories of an user (private).
        _organizations (int): number of public organizations where the user is (private).
        _join (str): when the user joined to GitHub. Format: %Y-%M-%DT%H:%i:%sZ (private).
        _avatar (str): URL where the user's avatar is (private).
        _bio (str): bio of the user (private).
    """

    def __init__(self, name, server="https://github.com/"):
        """Constructor of the class.
        Args:
            name (str): name (login) of an user in GitHub
            server (str): server to query data. Default: https://github.com/

        Returns:
            a new instance of GitHubUser class
        """
        self._name = name
        self._server = server
        self._followers = -1
        self._numRepos = -1
        self._organizations = -1
        self._contributions = -1
        self._join = ""
        self._avatar = ""
        self._bio = ""
        self._public = -1
        self._private = -1

    def export(self):
        """Export all attributes of the user to a dict
        Returns:
            dict with all attributes of the user
        """
        data = {}
        data["name"] = self.getName()
        data["contributions"] = self.getContributions()
        data["avatar"] = self.getAvatar()
        data["followers"] = self.getFollowers()
        data["join"] = self.getJoin()
        data["organizations"] = self.getOrganizations()
        data["repositories"] = self.getNumberOfRepositories()
        data["bio"] = self.getBio()
        data["private"] = self.getPrivateContributions()
        data["public"] = self.getPublicContributions()
        return data


    def getName(self):
        """Get the name of the user
        Returns:
            str with the name of the user
        """
        return self._name

    def getContributions(self):
        """Get the number of public contributions of the user
        Returns:
            int with the number of public contributions of the user
        """
        return self._contributions


    def getAvatar(self):
        """Get the URL where the avatar is

        Returns:
            str with an URL where the avatar is
        """
        return self._avatar

    def getFollowers(self):
        """Get the number of followers of this user

        Returns:
            int with the number of followers
        """
        return self._followers

    def getLocation(self):
        """Get the location of the user

        Returns:
            str with location of the user
        """
        return self._location

    def getJoin(self):
        """Get when an user joined to GitHub

        Returns:
            a str with this time format %Y-%M-%DT%H:%i:%sZ
        """
        return self._join

    def getOrganizations(self):
        """Get the number of public organizations where the user is

        Returns:
            int with the number of organizations

        """
        return self._organizations

    def getNumberOfRepositories(self):
        """Get the number of repositories of this user

        Returns:
            int with the number of repositories
        """
        return self._numRepos

    def getBio(self):
        """Get the bio of the user

        Returns:
            str with the bio
        """
        return self._bio

    def getPublicContributions(self):
        """Get only the public contributions of the user

        Returns:
            int with the number of public contributions
        """
        return self._public

    def getPrivateContributions(self):
        """Get the number of private contributions of the user

        Returns:
            int with the number of private contributions
        """
        return self._private

    def getData(self):
        """Get data of a GitHub user.
        """

        url = self._server + self._name

        data = self._getDataFromURL(url)

        web = BeautifulSoup(data,"lxml")

        contributions_raw = web.find_all('h2',{'class': 'f4 text-normal mb-2'})

        self._contributions = int(contributions_raw[0].text.lstrip().split(" ")[0].replace(",",""))

        #Avatar
        self._avatar = web.find("img", {"class":"avatar"})['src'][:-10]


        counters = web.find_all('span',{'class':'counter'})

        #Number of repositories
        self._numRepos = int(counters[0].text)

        #Followers
        self._followers = int(counters[2].text)

        #Location
        self._location = web.find("li", {"itemprop":"homeLocation"}).text

        #Date of creation
        join = dateutil.parser.parse(web.find("local-time",{"class":"join-date"})["datetime"])
        self._join = join.strftime("%Y-%m-%d %H:%M:%S %Z")

        #Bio
        bio = web.find_all("div",{"class":"user-profile-bio"})
        if len(bio)>0:
            self._bio = bio[0].text
        else:
            self._bio=""

        #Number of organizations
        self._organizations = len(web.find_all("a",{"class":"avatar-group-item"}))



    def getRealContributions(self):
        datefrom = datetime.datetime.now() - relativedelta(days=366)
        dateto = datefrom + relativedelta(months=1) - relativedelta(days=1)
        private = 0

        while datefrom < datetime.datetime.now():
            fromstr = datefrom.strftime("%Y-%m-%d")
            tostr = dateto.strftime("%Y-%m-%d")
            url = "https://github.com/"+self._name+"?tab=overview&from="+fromstr+"&to="+tostr
            data = self._getDataFromURL(url)
            web = BeautifulSoup(data,"lxml")


            ppcontributions = web.find_all('span',{'class':'m-0 text-gray'})

            for contrib in ppcontributions:
                private+=int(contrib.text.lstrip().strip(" ")[0])


            datefrom += relativedelta(months=1)
            dateto += relativedelta(months=1)

        self._private = private
        self._public = self._contributions - private




    def _getDataFromURL(self, url):
        """Read HTML data from an user GitHub profile (private).

        Note:
            This method is private.
            If max number of request is reached, method will stop some time.

        Args:
            url (str): URL to query.

        Returns:
            A str with the webpage
        """
        code = 0

        hdr = {'User-Agent': 'curl/7.43.0 (x86_64-ubuntu) libcurl/7.43.0 OpenSSL/1.0.1k zlib/1.2.8 gh-rankings-grx',
               'Accept': 'text/html',
               'Pragma': 'no-cache',
               'Connection': 'keep-alive',
               'X-PJAX': 'true'
               }

        while code != 200:
            req = urllib.request.Request(url, headers=hdr)
            try:
                response = urllib.request.urlopen(req)
                code = response.code
                time.sleep(0.01)
            except HTTPError as e:
                code = e.code
                if code == 404:
                    break;
            except URLError as e:
                time.sleep(3)

        if code == 404:
                raise Exception("User was not found")
        return response.read().decode('utf-8')
