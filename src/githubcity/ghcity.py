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
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from threading import Lock, Thread
from calendar import timegm
from queue import Queue, Empty
from time import sleep
from json import load, loads, dump
from logging import getLogger
from pystache import parse, Renderer
from coloredlogs import install
import datetime
from gzip import GzipFile
from io import BytesIO
from githubcity.ghuser import GitHubUser


class GitHubCity:
    """Manager of a GithubCity."""

    def __init__(self, githubID, githubSecret, configuration=False,
                 verbosity=0):
        """Constructor of the class.

        Constructor of the class GitHubCity.

        :param githubID: your GitHub ID.
        :type githubID: str.
        :param githubSecret: your GitHub Secret.
        :type githubSecret: str.
        :param configuration: configuration of the class.
        :type configuration: dict.

        Note
        ----------
            To get your ID and secret, you will need to create
            an application in
            https://github.com/settings/applications/new
        """
        self.__logger = getLogger("GitHubCity")
        self.__logger.info("Starting GitHubCity")
        install(level=verbosity)

        if not githubID:
            self.__logger.exception("init: No GitHub ID inserted")
            raise Exception("init: No GitHub ID inserted")
        self.__githubID = githubID

        if not githubSecret:
            self.__logger.exception("init: No GitHub Secret inserted")
            raise Exception("init: No GitHub Secret inserted")
        self.__githubSecret = githubSecret

        self.__usersToProccess = Queue()
        self.__urlLocations = ""
        self.__urlFilters = ""
        self.__cityUsers = set()
        self.__processedUsers = []
        self.__threads = set()
        self.__end = False
        self.__lastDay = False
        self.__lockGetUser = Lock()
        self.__lockReadAddUser = Lock()
        self.__server = "https://api.github.com/"
        self.__intervals = []
        self.__excludedUsers= []
        self.__excludedLocations = []

        if configuration:
            self.readConfig(configuration)
            self.__logger.debug("Configuration set")
        else:
            self.__logger.warning("Not configuration set")

    # Read configurations ----------------------------------------------------
    def readConfig(self, configuration):
        """Read configuration from dict.

        Read configuration from a JSON configuration file.

        :param configuration: configuration to load.
        :type configuration: dict.
        """
        self.__logger.debug("Reading configuration")
        self.city = configuration["name"]
        self.__logger.info("City name: " + self.city)
        if "intervals" in configuration:
            self.__intervals = configuration["intervals"]
            self.__logger.debug("Intervals: " +
                                str(self.__intervals))

        if "last_date" in configuration:
            self.__lastDay = configuration["last_date"]
            self.__logger.debug("Last day: " + self.__lastDay)

        if "locations" in configuration:
            self.__locations = configuration["locations"]
            self.__logger.debug("Locations: " +
                                str(self.__locations))
            self.__addLocationsToURL(self.__locations)

        if "excludedUsers" in configuration:
            self.__excludedUsers= set()
            self.__excludedLocations = set()

            excluded = configuration["excludedUsers"]
            for e in excluded:
                self.__excludedUsers.add(e)
            self.__logger.debug("Excluded users " +
                                str(self.__excludedUsers))

        if "excludedLocations" in configuration:
            excluded = configuration["excludedLocations"]
            for e in excluded:
                self.__excludedLocations.add(e)

            self.__logger.debug("Excluded locations " +
                                str(self.__excludedLocations))

    def readConfigFromJSON(self, fileName):
        """Read configuration from JSON.

        :param fileName: path to the configuration file.
        :type fileName: str.
        """
        self.__logger.debug("readConfigFromJSON: reading from " + fileName)
        with open(fileName) as data_file:
            data = load(data_file)
        self.readConfig(data)

    def configToJson(self, fileName):
        """Save the configuration of the city in a JSON.

        :param fileName: path to the output file.
        :type fileName: str.
        """
        config = self.getConfig()
        with open(fileName, "w") as outfile:
            dump(config, outfile, indent=4, sort_keys=True)

    def getConfig(self):
        """Return the configuration of the city.

        :return: configuration of the city.
        :rtype: dict.
        """
        config = {}
        config["name"] = self.city
        config["intervals"] = self.__intervals
        config["last_date"] = self.__lastDay
        config["excludedUsers"] = []
        config["excludedLocations"] = []

        for e in self.__excludedUsers:
            config["excludedUsers"].append(e)

        for e in self.__excludedLocations:
            config["excludedLocations"].append(e)

        config["locations"] = self.__locations
        return config
    # En read configurations --------------------------------------------------

    # Get and process users ---------------------------------------------------
    def addFilter(self, field, value):
        """Add a filter to the seach.

        :param field: what field filter (see GitHub search).
        :type field: str.
        :param value: value of the filter (see GitHub search).
        :type value: str.
        """
        if "<" not in value or ">" not in value or ".." not in value:
            value = ":" + value

        if self.__urlFilters:
            self.__urlFilters += "+" + field + str(quote(value))
        else:
            self.__urlFilters += field + str(quote(value))

    def __processUsers(self):
        """Process users of the queue."""
        while self.__usersToProccess.empty() and not self.__end:
            pass

        while not self.__end or not self.__usersToProccess.empty():
            self.__lockGetUser.acquire()
            try:
                new_user = self.__usersToProccess.get(False)
            except Empty:
                self.__lockGetUser.release()
                return
            else:
                self.__lockGetUser.release()
                self.__addUser(new_user)
                self.__logger.info("__processUsers:" +
                                   str(self.__usersToProccess.qsize()) +
                                   " users to  process")

    def __addUser(self, new_user):
        """Add new users to the list.

        :param new_user: name of a GitHub user to include in
            the ranking
        :type new_user: str.
        """
        self.__lockReadAddUser.acquire()
        if new_user not in self.__cityUsers and \
                new_user not in self.__excludedUsers:
            self.__lockReadAddUser.release()
            self.__logger.debug("__addUser: Adding " + new_user)
            self.__cityUsers.add(new_user)

            myNewUser = GitHubUser(new_user)
            myNewUser.getData()
            myNewUser.getRealContributions()

            userLoc = myNewUser.location
            if not any(s in userLoc for s in self.__excludedLocations):
                self.__processedUsers.append(myNewUser)
        else:
            self.__logger.debug("__addUser: Excluding " + new_user)
            self.__lockReadAddUser.release()

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
                self.__usersToProccess.put(u["login"])
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

        self.__end = False
        self.__threads = set()

        comprobationURL = self.__getURL()
        self.__readAPI(comprobationURL)

        self.__launchThreads(numberOfThreads)
        self.__logger.debug("Launching threads")
        for i in self.__intervals:
            self.__getPeriodUsers(i[0], i[1])

        self.__end = True

        for t in self.__threads:
            t.join()
        self.__logger.debug("Threads joined")
    # End of get and process users --------------------------------------------

    # Calcule and set intervals----------------------------------------------
    def calculateBestIntervals(self):
        """Calcule valid intervals of a city."""
        self.__intervals = []
        self.__readAPI(self.__getURL())
        today = datetime.datetime.now().date()

        self.__validInterval(datetime.date(2008, 1, 1), today)
        self.__logger.info("Total number of intervals: " +
                           str(len(self.__intervals)))
        self.__lastDay = today.strftime("%Y-%m-%d")

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
    # End calcule and set intervals-------------------------------------------

    # Import/export users ----------------------------------------------------
    def export(self, template_file_name, output_file_name,
               sort="public", data=None, limit=0):
        """Export ranking to a file.

        Args:
            template_file_name (str): where is the template
                (moustache template)
            output_file_name (str): where create the file with the ranking
            sort (str): field to sort the users
        """
        exportedData = {}
        exportedUsers = self.__exportUsers(sort, limit)

        exportedData["users"] = exportedUsers
        exportedData["extraData"] = data

        with open(template_file_name) as template_file:
            template_raw = template_file.read()

        template = parse(template_raw)
        renderer = Renderer()

        output = renderer.render(template, exportedData)

        with open(output_file_name, "w") as text_file:
            text_file.write(output)

    def getSortedUsers(self, order="public"):
        """Return a list with sorted users.

        :param order: the field to sort the users.
            - contributions (total number of contributions)
            - public (public contributions)
            - private (private contributions)
            - name
            - followers
            - join
            - organizations
            - repositories
        :type order: str.
        :return: a list of the github users sorted by the selected field.
        :rtype: str.
        """
        try:
            self.__processedUsers.sort(key=lambda u: getattr(u, order), reverse=True)
        except AttributeError:
            pass
        return self.__processedUsers

    def __exportUsers(self, sort, limit=0):
        """Export the users to a dictionary.

        :param sort: field to sort the users
        :type sort: str.
        :return: exported users.
        :rtype: dict.
        """
        position = 1
        dataUsers = self.getSortedUsers(sort)

        if limit:
            dataUsers = dataUsers[:limit]

        exportedUsers = []

        for u in dataUsers:
            userExported = u.export()
            userExported["position"] = position
            exportedUsers.append(userExported)

            if position < len(dataUsers):
                userExported["comma"] = True

            position += 1
        return exportedUsers

    # End import/export users ------------------------------------------------

    # Utilities --------------------------------------------------------------
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
             + str(quote(l)) + "\""

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
            newThr = Thread(target=self.__processUsers)
            newThr.setDaemon(True)
            self.__threads.add(newThr)
            newThr.start()

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
               'Accept': 'application/vnd.github.v3.text-match+json',
               'Accept-Encoding': 'gzip'}
        while code != 200:
            req = Request(url, headers=hdr)
            try:
                self.__logger.debug("Getting " + url)
                response = urlopen(req)
                code = response.code
            except HTTPError as error:
                if error.code == 404:
                    self.__logger.exception("_readAPI: ERROR 404")
                    self.__logger.exception(str(error))
                    break
                headers = error.headers.items()
                reset = -1
                for header in headers:
                    if header[0] == "X-RateLimit-Reset":
                        reset = int(header[1])
                if reset < 0:
                    log_message = "Error when reading response. Wait: 30 secs"
                    sleep_duration = 30
                else:
                    utcAux = datetime.datetime.utcnow()
                    utcAux = utcAux.utctimetuple()
                    now_sec = timegm(utcAux)
                    sleep_duration = reset - now_sec
                    log_message = "Limit of API. Wait: "
                    log_message += str(sleep_duration)
                    log_message += " secs"
                self.__logger.warning(log_message)
                sleep(sleep_duration)
                code = 0
            except URLError as error:
                self.__logger.exception(str(error))
                self.__logger.exception("_readAPI: waiting 15 secs")
                sleep(15)
        responseBody = response.read()

        if response.getheader('Content-Encoding') == 'gzip':
            with GzipFile(fileobj=BytesIO(responseBody)) as gzFile:
                responseBody = gzFile.read()

        data = loads(responseBody.decode('utf-8'))
        response.close()
        return data

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
                self.__urlFilters + \
                "&sort=joined&order=asc&per_page=100&page=" + \
                str(page)
        else:
            url = self.__server + "search/users?client_id=" + \
                self.__githubID + "&client_secret=" + \
                self.__githubSecret + \
                "&order=desc&q=sort:joined+type:user" + \
                self.__urlLocations + \
                self.__urlFilters + \
                "+created:" + \
                start_date + ".." + final_date + \
                "&sort=joined&order=" + order + \
                "&per_page=100&page=" + str(page)
        return url
    # Endf utilities ----------------------------------------------------------
