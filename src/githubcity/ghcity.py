"""Allows to get all data about a given GitHub City.

This module allow to developers to get all users of GitHub that have a
given city in their profile. For example, if I want getting all users
from London,. I will get all users that have London in their
profiles (they could live in London or not)

Author: Israel Blancas @iblancasa
Original idea: https://github.com/JJ/github-city-rankings
License:

The MIT License (MIT)
    Copyright (c) 2015-2017 Israel Blancas @iblancasa (http://iblancasa.com/)

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the Software), to deal in the Software
    without restriction, including without
    limitation the rights to use, copy, modify, merge,
    publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
    PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
    USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import absolute_import
import urllib.request
import urllib.parse
import threading
import datetime
import calendar
import queue
import time
import json
import logging
import pystache
import coloredlogs


class GitHubCity:
    """Manager of a GithubCity."""

    def __init__(self, githubID, githubSecret, configuration, verbosity=0):
        """Constructor of the class.

        Constructor of the class GitHubCity.

        :param githubID: your GitHub ID.
        :type githubID: str.
        :param githubSecret: your GitHub Secret.
        :type githubSecret: str.
        :param configuration: configuration of the class
        :type configuration: dict.

        Note
        ----------
            To get your ID and secret, you will need to create
            an application in
            https://github.com/settings/applications/new
        """
        self.__logger = logging.getLogger("GitHubCity")
        self.__logger.info("Starting GitHubCity")
        coloredlogs.install(level=verbosity)

        if not githubID:
            self.__logger.exception("init: No GitHub ID inserted")
            raise Exception("init: No GitHub ID inserted")
        self.__githubID = githubID

        if not githubSecret:
            self.__logger.exception("init: No GitHub Secret inserted")
            raise Exception("init: No GitHub Secret inserted")
        self.__githubSecret = githubSecret

        self.__names = queue.Queue()
        self.__urlLocations = ""
        self.__myusers = set()
        self.__dataUsers = []
        self.__threads = set()
        self.__fin = False
        self.__lastDay = False
        self.__lockGetUser = threading.Lock()
        self.__lockReadAddUser = threading.Lock()
        self.__server = "https://api.github.com/"
        self.readConfig(configuration)

    def readConfig(self, configuration):
            """Read configuration from dict.

            Read configuration from a JSON configuration file.

            :param configuration: configuration to load.
            :type configuration: dict.
            """
            self.__logger.debug("Reading configuration")
            self.__city = configuration["name"]
            self.__logger.info("City name: " + self.__city)
            self.__intervals = configuration["intervals"]
            self.__logger.debug("Intervals: " +
                                str(self.__intervals))
            self.__lastDay = configuration["last_date"]
            self.__logger.debug("Last day: " + self.__lastDay)
            self.__locations = configuration["locations"]
            self.__logger.debug("Locations: " +
                                str(self.__locations))
            self.__excluded = set()
            self.__excludedLocations = set()

            excluded = configuration["excludedUsers"]
            for e in excluded:
                self.__excluded.add(e)

            self.__logger.debug("Excluded users " +
                                str(self.__excluded))

            excluded = configuration["excludedLocations"]
            for e in excluded:
                self.__excludedLocations.add(e)

            self.__logger.debug("Excluded locations " +
                                str(self.__excludedLocations))

            self.__addLocationsToURL(self.__locations)

    def calculeToday(self):
        """Calcule the intervals from the last date."""
        self.__logger.debug("Add today")
        last = datetime.datetime.strptime(self.__lastDay, "%Y-%m-%d")
        today = datetime.datetime.now().date()
        self.__validInterval(last, today)

    def __addLocationsToURL(self, locations):
        """Format all locations to GitHub's URL API.

        :param locations: locations where to search users.
        :type locations: list(str).
        """
        for l in self.__locations:
            self.__urlLocations += "+location:\""\
             + str(urllib.parse.quote(l)) + "\""

    def __processUsers(self):
        """Process users of the queue."""
        while self.__names.empty() and not self.__fin:
            pass

        while not self.__fin or not self.__names.empty():
            self.__lockGetUser.acquire()
            try:
                new_user = self.__names.get(False)
            except queue.Empty:
                self.__lockGetUser.release()
                return
            else:
                self.__lockGetUser.release()
                self.__addUser(new_user)
                self.__logger.info("_processUsers:" +
                                   str(self.__names.qsize()) +
                                   " users to  process")

    def _addUser(self, new_user):
        """Add new users to the list.

        :param new_user: name of a GitHub user to include in
            the ranking
        :type new_user: str.
        """
        self._lockReadAddUser.acquire()
        if new_user not in self._myusers and \
                new_user not in self._excluded:
            self._lockReadAddUser.release()
            self._logger.log(6, "_addUser: Adding " + new_user)
            self._myusers.add(new_user)

            myNewUser = GitHubUser(new_user)
            myNewUser.getData()
            myNewUser.getRealContributions()

            userLoc = myNewUser.getLocation()
            if not any(s in userLoc for s in self._excludedLocations):
                self._dataUsers.append(myNewUser)
        else:
            self._logger.log(6, "_addUser: Excluding " + new_user)
            self._lockReadAddUser.release()

    def __launchThreads(self, numThreads):
        """Launch some threads and start to process users.

        :param numThreads: number of thrads to launch.
        :type numThreads: int.
        """
        i = 0
        while i < numThreads:
            self.__logger.debug("Launching thread number " +
                                str(i))
            i += 1
            newThr = threading.Thread(target=self.__processUsers)
            newThr.setDaemon(True)
            self.__threads.add(newThr)
            newThr.start()

    def __getPeriodUsers(self, start_date, final_date):
        """Get all the users given a period.

        :param start_date: start date of the range to search
            users
        :type start_date: time.date.
        :param final_date: final date of the range to search
            users
        :type final_date: time.date.
        """
        self.__logger.info("Getting users from " + start_date +
                           " to " + final_date)

        url = self.__getURL(1, start_date, final_date)
        data = self.__readAPI(url)
        users = []

        total_pages = 10000
        page = 1

        while total_pages >= page:
            url = self.__getURL(page, start_date, final_date)
            data = self.__readAPI(url)
            self.__logger.debug(str(len(data['items'])) +
                                " users found")
            for u in data['items']:
                users.append(u["login"])
                self.__names.put(u["login"])
            total_count = data["total_count"]
            total_pages = int(total_count / 100) + 1
            page += 1
        return users

    def getCityUsers(self, numberOfThreads=20):
        """Get all the users from the city.

        :param numberOfThreads: number of threads to run.
        :type numberOfThreads: int.
        """
        if not self.__intervals:
            self.__logger.debug("Calculating best intervals")
            self.calculateBestIntervals()

        self.__fin = False
        self.__threads = set()

        comprobationURL = self.__getURL()
        self.__readAPI(comprobationURL)

        self.__launchThreads(numberOfThreads)
        self.__logger.debug("Launching threads")
        for i in self.__intervals:
            self.__getPeriodUsers(i[0], i[1])

        self.__fin = True

        for t in self.__threads:
            t.join()
        self.__logger.debug("Threads joined")

    def __getURL(self, page=1, start_date=None,
                 final_date=None, order="asc"):
        """Get the API's URL to query to get data about users.

        :param page: number of the page.
        :param start_date: start date of the range to search
            users (Y-m-d).
        "param final_date: final date of the range to search
            users (Y-m-d).
        :param order: order of the query. Valid values are
            'asc' or 'desc'. Default: asc
        :return: formatted URL.
        :rtype: str.
        """
        if not start_date or not final_date:
            url = self.__server + "search/users?client_id=" + \
                self.__githubID + "&client_secret=" + \
                self.__githubSecret + \
                "&order=desc&q=sort:joined+type:user" + \
                self.__urlLocations + \
                "&sort=joined&order=asc&per_page=100&page=" + \
                str(page)
        else:
            url = self.__server + "search/users?client_id=" + \
                self.__githubID + "&client_secret=" + \
                self.__githubSecret + \
                "&order=desc&q=sort:joined+type:user" + \
                self.__urlLocations + "+created:" + \
                start_date + ".." + final_date + \
                "&sort=joined&order=" + order + \
                "&per_page=100&page=" + str(page)
        return url

    def __readAPI(self, url):
        """Read a petition to the GitHub API (private).

        :param url: URL to query.
        :type url: str.
        :return: the response of the API -a dictionary with
            these fields-:
            * total_count (int): number of total
            users that match with the search
            * incomplete_results (bool):
            https://developer.github.com/v3/search/#timeouts-and-incomplete-results
            * items (List[dict]): a list with the
            users that match with the search
        :rtype: dict.
        """
        code = 0
        hdr = {'User-Agent': 'curl/7.43.0 (x86_64-ubuntu) \
               libcurl/7.43.0 OpenSSL/1.0.1k zlib/1.2.8 gh-rankings-grx',
               'Accept': 'application/vnd.github.v3.text-match+json'}
        while code != 200:
            req = urllib.request.Request(url, headers=hdr)
            try:
                self.__logger.debug("Getting " + url)
                response = urllib.request.urlopen(req)
                code = response.code
            except urllib.error.URLError as e:
                if hasattr(e, "getheader"):
                    reset = int(e.getheader("X-RateLimit-Reset"))
                    utcAux = datetime.datetime.utcnow()
                    utcAux = utcAux.utctimetuple()
                    now_sec = calendar.timegm(utcAux)
                    log_message = "Limit of API. Wait: "
                    log_message += str(reset - now_sec)
                    log_message += " secs"
                    self.__logger.warning(log_message)
                    time.sleep(reset - now_sec)
                code = 0
            except Exception as e:
                self.__logger.exception("_readAPI: waiting 10 secs")
                time.sleep(10)

        data = json.loads(response.read().decode('utf-8'))
        response.close()
        return data

    def __validInterval(self, start, finish):
            """Check if the interval is correct.

            An interval is correct if it has less than 1001
            users. If the interval is correct, it will be added
            to '_intervals' attribute. Else, interval will be
            split in two news intervals and these intervals
            will be checked.

            :param start: start date of the interval.
            :type start: datetime.date.
            :param finish: finish date of the interval.
            :type finish: datetime.date.
            """
            url = self.__getURL(1,
                                start.strftime("%Y-%m-%d"),
                                finish.strftime("%Y-%m-%d"))

            data = self.__readAPI(url)

            if data["total_count"] >= 1000:
                middle = start + (finish - start)/2
                self.__validInterval(start, middle)
                self.__validInterval(middle, finish)
            else:
                self.__intervals.append([start.strftime("%Y-%m-%d"),
                                        finish.strftime("%Y-%m-%d")])
                self.__logger.info("New valid interval: " +
                                   start.strftime("%Y-%m-%d") +
                                   " to " +
                                   finish.strftime("%Y-%m-%d"))

    def calculateBestIntervals(self):
        """Calcule valid intervals of a city."""
        self.__intervals = []
        self.__readAPI(self._getURL())
        today = datetime.datetime.now().date()

        self.__validInterval(datetime.date(2008, 1, 1), today)
        self.__logger.info(
                           "Total number of intervals: " +
                           str(len(self.__intervals)))
        self.__lastDay = today.strftime("%Y-%m-%d")

    def readConfigFromJSON(self, fileName):
        """Read configuration from JSON.

        :param fileName: path to the configuration file.
        :type fileName: str.
        """
        self.__logger.debug("readConfigFromJSON: reading from " + fileName)
        with open(fileName) as data_file:
            data = json.load(data_file)
        self.readConfig(data)
