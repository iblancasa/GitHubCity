#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This module allow to developers to get all users of GitHub that have a given
city in their profile. For example, if I want getting all users from London,
I will get all users that have London in their profiles (they could live in London or not)

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

import urllib.request
import urllib.parse
import threading
import datetime
import calendar
import time
import queue
import pystache
import json
from urllib.error import HTTPError
from dateutil.relativedelta import relativedelta
import os
from multiprocessing import Lock
import sys
import logging
import coloredlogs
sys.path.append(os.getcwd())
from githubcity import ghuser
GitHubUser = ghuser.GitHubUser

class GitHubCity:
    """Manager of a GithubCity.

    Attributes:
        _city (str): Name of the city (private).
        _myusers (set): Name of all users in a city (private).
        _githubID (str): ID of your GitHub application (private).
        _githubSecret (str): secretGH of your GitHub application (private).
        _dataUsers (List[GitHubUser]): the list of GitHub users (private).
        _excluded (set): set of names of excluded users (private).
        _excludedLocations (set): set of excluded locations (private).
        _lastDay (str): day of last interval (private).
        _names (Queue): Queue with all users that we still have to process (private).
        _threads (set): Set of active Threads (private).
        _logger (logger): Logger (private).
        _lockGetUser (Lock): lock to solve problems with threads in get user (private).
        _lockReadAddUser (Lock): lock to solve problems with threads in check if an user is repeated(private).
        _fin (bool): check if there are more users to process (private).
        _locations (list): list of locations where search users (private).
        __urlLocations (str): string with the locations formatted to GitHub API URL (private).

    """


    def __init__(self, githubID, githubSecret, config=None, city=None, locations=None,
                excludedUsers=None, excludedLocations=None, debug=False):
        """Constructor of the class.

        Note:
            To get your ID and secret, you will need to create an application in
            https://github.com/settings/applications/new .

        Args:
            githubID (str): ID of your GitHub application.
            githubSecret (str): Secret of your GitHub application.
            city (str): Name of the city you want to search about (optional).
            config (dict): set with configuration (see cityconfigschema.json)
            locations (list): locations where search users (optional).
            excludedUsers (dir): excluded users of the ranking (optional).
            excludedLocations (list): excluded locations (optional).
            debug (bool): show a log in your terminal (optional).

        Returns:
            a new instance of GithubCity class

        """

        if githubID==None:
            raise Exception("No GitHub ID inserted")
        self._githubID = githubID

        if githubSecret==None:
            raise Exception("No GitHub Secret inserted")
        self._githubSecret = githubSecret

        self._names = queue.Queue()
        self._myusers = set()
        self._dataUsers = []
        self._threads = set()
        self._logger = logging.getLogger("GitHubCity")

        if debug:
            coloredlogs.install(level='DEBUG')

        self._fin = False
        self._lockGetUser = Lock()
        self._lockReadAddUser = Lock()

        if config:
            self.readConfig(config)
            self._addLocationsToURL(self._locations)
        else:
            self._city = city
            self._locations  = locations
            self._intervals=[]

            if not self._locations:
                self._locations = []
                if self._city:
                    self._locations.append(self._city)

            self._addLocationsToURL(self._locations)

            self._excluded = set()
            if excludedUsers:
                for e in excludedUsers:
                    self._excluded.add(e)


            self._excludedLocations = set()
            if excludedLocations:
                for e in excludedLocations:
                    self._excludedLocations.add(e)



    def __str__(self):
        """str the class"""
        return str(self.getConfig())

    def _addLocationsToURL(self, locations):
        """Format all locations to GitHub's URL API

        Note:
            This method is private.

        Args:
            locations (list): list of str where each str is a location where search
        """
        self._urlLocations = ""

        for l in self._locations:
            self._urlLocations += "+location:\"" + str(urllib.parse.quote(l))+"\""


    def readConfig(self, config):
        """Read config from a dict

        Args:
            config: config to read (see cityconfigschema.json)
        """
        self._city = config["name"]
        self._intervals = config["intervals"]
        self._lastDay = config["last_date"]
        self._locations = config["locations"]
        self._excluded = set()
        self._excludedLocations = set()

        excluded = config["excludedUsers"]
        for e in excluded:
            self._excluded.add(e)

        excluded = config["excludedLocations"]
        for e in excluded:
            self._excludedLocations.add(e)

        self._addLocationsToURL(self._locations)
        last = datetime.datetime.strptime(self._lastDay, "%Y-%m-%d")
        today = datetime.datetime.now().date()

        self._validInterval(last, today)




    def readConfigFromJSON(self, fileName):
        """Read configuration from a file

        Args:
            fileName (str): name of a config file (see cityconfigschema.json)
        """
        with open(fileName) as data_file:
            data = json.load(data_file)
        self.readConfig(data)

    def _addUser(self, new_user):
        """Add new users to the list (private).

        Note:
            This method is private.
            If the user is yet in the list (or in excluded users list), he/she will not be added

        Args:
            new_user (str): name of a GitHub user to include in the ranking

        """
        self._lockReadAddUser.acquire()
        if not new_user in self._myusers and not new_user in self._excluded:
            self._lockReadAddUser.release()
            self._myusers.add(new_user)
            myNewUser = GitHubUser(new_user)
            myNewUser.getData()

            userLoc = myNewUser.getLocation()
            if not any(s in userLoc for s in self._excludedLocations):
                self._dataUsers.append(myNewUser)
        else:
            self._lockReadAddUser.release()



    def _readAPI(self, url):
        """Read a petition to the GitHub API (private).

        Note:
            This method is private.
            If max number of request is reached, method will some time (header says).

        Args:
            url (str): URL to query.

        Returns:
            The response of the API -a dictionary with these fields-:
                * total_count (int): number of total users that match with the search
                * incomplete_results (bool): https://developer.github.com/v3/search/#timeouts-and-incomplete-results
                * items (List[dict]): a list with the users that match with the search
        """

        code = 0
        hdr = {'User-Agent': 'curl/7.43.0 (x86_64-ubuntu) libcurl/7.43.0 OpenSSL/1.0.1k zlib/1.2.8 gh-rankings-grx',
               'Accept': 'application/vnd.github.v3.text-match+json'
               }
        while code != 200:
            req = urllib.request.Request(url, headers=hdr)
            try:
                response = urllib.request.urlopen(req)
                code = response.code
            except urllib.error.URLError as e:
                if hasattr(e,"getheader"):
                    reset = int(e.getheader("X-RateLimit-Reset"))
                    now_sec = calendar.timegm(datetime.datetime.utcnow().utctimetuple())
                    self._logger.warning("Limit of API. Wait: "+str(reset - now_sec)+" secs")
                    time.sleep(reset - now_sec)
                code = e.code

        data = json.loads(response.read().decode('utf-8'))
        response.close()
        return data



    def _getURL(self, page=1, start_date=None, final_date=None,order="asc"):
        """Get the API's URL to query to get data about users (private).

        Note:
            This method is private.

        Args:
            page (int): number of the page.
            start_date (str): start date of the range to search users (Y-m-d).
            final_date (str): final date of the range to search users (Y-m-d).
            order (str): order of the query. Valid values are 'asc' or 'desc'. Default: asc

        Returns:
            The URL (str) to query.

        """
        if not start_date or not final_date:
            url = "https://api.github.com/search/users?client_id=" + self._githubID + "&client_secret=" + self._githubSecret + \
                "&order=desc&q=sort:joined+type:user" + self._urlLocations + \
                "&sort=joined&order=asc&per_page=100&page=" + str(page)
        else:
            url = "https://api.github.com/search/users?client_id=" + self._githubID + "&client_secret=" + self._githubSecret + \
                "&order=desc&q=sort:joined+type:user" + self._urlLocations + \
                "+created:" + start_date +\
                ".." + final_date +\
                "&sort=joined&order="+order+"&per_page=100&page=" + str(page)
        return url



    def _processUsers(self):
        """Process users of the queue (get from the queue an add user) (private)

            Note:
                This method is private.

        """
        while(self._names.empty() and not self._fin):
            pass

        while not self._fin or not self._names.empty():
            self._lockGetUser.acquire()
            try:
                new_user = self._names.get(False)
            except queue.Empty:
                self._lockGetUser.release()
                return
            else:
                self._lockGetUser.release()
                self._addUser(new_user)
                self._logger.debug(str(self._names.qsize())+" users to process")



    def _launchThreads(self, numThreads):
        """Launch some threads and call to 'processUsers' (private)

        Note:
            This method is private.

        """
        i = 0
        while i<numThreads:
            i+=1
            newThr = threading.Thread(target=self._processUsers)
            newThr.setDaemon(True)
            self._threads.add(newThr)
            newThr.start()



    def _getPeriodUsers(self, start_date, final_date):
        """Get all the users given a period (private).

        Note:
            This method is private.
            User's names are added to the private _name attribute.

        Args:
            start_date (datetime.date): start date of the range to search users.
            final_date (datetime.date): final date of the range to search users.

        """
        self._logger.info("Getting users from " + start_date + " to " + final_date)

        url = self._getURL(1, start_date, final_date)
        data = self._readAPI(url)

        total_pages = 10000
        page = 1

        while total_pages>=page:
            url = self._getURL(page, start_date, final_date)
            data = self._readAPI(url)
            
            for u in data['items']:
                self._names.put(u["login"])
            total_count = data["total_count"]
            total_pages = int(total_count / 100) + 1
            page += 1



    def getCityUsers(self):
        """Get all the users from the city.
        """
        if len(self._intervals)==0:
            self.calculateBestIntervals()

        self._fin = False
        self._threads = set()

        comprobationURL = self._getURL()
        comprobationData = self._readAPI(comprobationURL)

        self._launchThreads(20)

        for i in self._intervals:
            self._getPeriodUsers(i[0], i[1])

        self._fin = True

        for t in self._threads:
            t.join()



    def _validInterval(self, start, finish):
        """Given a valid interval, check if the interval is correct (less than 1000 users).
        If the interval is correct, it will be added to '_intervals' attribute. Else,
        interval will be split in two news intervals and these intervals will be
        checked.

        Args:
            start (datetime.date): start date of the interval
            finish (datetime.date): finish date of the interval

        Note:
            This method is private.
            Valid periods are added to the private _intervals attribute.

        """
        data = self._readAPI(self._getURL(1,start.strftime("%Y-%m-%d"),finish.strftime("%Y-%m-%d")))
        if data["total_count"]>=1000:
            middle = start + (finish - start)/2
            self._validInterval(start,middle)
            self._validInterval(middle,finish)
        else:
            self._intervals.append([start.strftime("%Y-%m-%d"),finish.strftime("%Y-%m-%d")])
            self._logger.debug("Valid interval: "+start.strftime("%Y-%m-%d")+" to "+\
            finish.strftime("%Y-%m-%d"))



    def calculateBestIntervals(self):
        """Calcules valid intervals of a city (with less than 1000 users)
        """
        comprobation = self._readAPI(self._getURL())
        self._bigCity = True
        self._validInterval(datetime.date(2008, 1, 1), datetime.datetime.now().date())
        self._logger.info("Total number of intervals: "+ str(len(self._intervals)))
        self._lastDay = datetime.datetime.now().date().strftime("%Y-%m-%d")


    def getTotalUsers(self):
        """Get the number of calculated users
        Returns:
            Number (int) of calculated users
        """
        return len(self._dataUsers)



    def getSortedUsers(self, order="contributions"):
        """Returns a list with sorted users.

        Args:
            order (str): a str with one of these values (field to sort by).
                - contributions
                - name
                - lstreak
                - cstreak
                - language
                - followers
                - join:
                - organizations
                - repositories
                - stars

        Returns:
            str with a list of GitHubUsers by the field indicate. If
            an invalid field is given, the result will be None

        """
        if order == "contributions":
            self._dataUsers.sort(key=lambda u: u.getContributions(), reverse=True)
        elif order == "name":
            self._dataUsers.sort(key=lambda u: u.getName(), reverse=True)
        elif order == "lstreak":
            self._dataUsers.sort(key=lambda u: u.getLongestStreak(), reverse=True)
        elif order == "cstreak":
            self._dataUsers.sort(key=lambda u: u.getCurrentStreak(), reverse=True)
        elif order == "language":
            self._dataUsers.sort(key=lambda u: u.getLanguage(), reverse=True)
        elif order == "followers":
            self._dataUsers.sort(key=lambda u: u.getFollowers(), reverse=True)
        elif order == "join":
            self._dataUsers.sort(key=lambda u: u.getJoin(), reverse=True)
        elif order == "organizations":
            self._dataUsers.sort(key=lambda u: u.getOrganizations(), reverse=True)
        elif order == "repositories":
            self._dataUsers.sort(key=lambda u: u.getNumberOfRepositories(), reverse=True)
        elif order == "stars":
            self._dataUsers.sort(key=lambda u: u.getStars(), reverse=True)
        return self._dataUsers


    def getConfig(self):
        """Returns the configuration of the city

        Returns:
            configuration of the city (dict)
        """
        config = {}
        config["name"] = self._city
        config["intervals"] = self._intervals
        config["last_date"] = self._lastDay
        config["excludedUsers"]=[]
        config["excludedLocations"]=[]

        for e in self._excluded:
            config["excludedUsers"].append(e)

        for e in self._excludedLocations:
            config["excludedLocations"].append(e)

        config["locations"]=self._locations
        return config


    def configToJson(self, fileName):
        """Saves the configuration of the city in a json

        Args:
            fileName (str): where save the configuration
        """
        config = self.getConfig()
        with open(fileName, "w") as outfile:
            json.dump(config, outfile, indent=4, sort_keys=True)


    def export(self, template_file_name, output_file_name, sort):
        """Export ranking to a file

        Args:
            template_file_name (str): where is the template (moustache template)
            output_file_name (str): where create the file with the ranking
            sort (str): field to sort the users
        """
        exportedData = {}
        dataUsers = self.getSortedUsers(sort)
        exportedUsers = []

        position = 1

        for u in dataUsers:
            userExported = u.export()
            userExported["position"] = position
            exportedUsers.append(userExported)

            if position  < len(dataUsers):
                userExported["comma"] = True

            position+=1


        exportedData["users"] = exportedUsers

        with open(template_file_name) as template_file:
            template_raw = template_file.read()

        template = pystache.parse(template_raw)
        renderer = pystache.Renderer()

        output = renderer.render(template, exportedData)

        with open(output_file_name, "w") as text_file:
            text_file.write(output)
