"""
Allows to get all data about a given GitHub user.

Author: Israel Blancas @iblancasa
Original idea: https://github.com/JJ/github-city-rankings
License:

The MIT License (MIT)
    Copyright (c) 2015 Israel Blancas @iblancasa (http://iblancasa.com/)

    Permission is hereby granted, free of charge, to any
    person obtaining a copy of this software
    and associated documentation files (the "Software"), to
    deal in the Software without restriction, including without
    limitation the rights to use, copy, modify, merge, publish,
    distribute, sublicense, and/or sell copies of the
    Software, and to permit persons to whom
    the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall
    be included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
    ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT
    OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import absolute_import
import time
import urllib.request
from urllib.error import HTTPError, URLError
import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup


class GitHubUser:
    """Manager of a GitHub User.

    Attributes:
        _name (str): Name of the user (private).
        _contributions (int): total contributions (web - last year) (private).
        _public (int): public contributions in the last year (private).
        _private (int): private contributions in the last year (private).
        _followers (int): total number of followers of an user (private).
        _numRepos (int): number of repositories of an user (private).
        _organizations (int): number of public organizations (private).
        _join (str): when the user joined. Format: %Y-%M-%D (private).
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
        self._public = 0
        self._private = 0
        self._location = ""

    def export(self):
        """Export all attributes of the user to a dict.

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
        """Get the name of the user.

        Returns:
            str with the name of the user
        """
        return self._name

    def getContributions(self):
        """Get the number of public contributions of the user.

        Returns:
            int with the number of public contributions of the user
        """
        return self._contributions

    def getAvatar(self):
        """Get the URL where the avatar is.

        Returns:
            str with an URL where the avatar is
        """
        return self._avatar

    def getFollowers(self):
        """Get the number of followers of this user.

        Returns:
            int with the number of followers
        """
        return self._followers

    def getLocation(self):
        """Get the location of the user.

        Returns:
            str with location of the user
        """
        return self._location

    def getJoin(self):
        """Get when an user joined to GitHub.

        Returns:
            a str with this time format %Y-%M-%DT%H:%i:%sZ
        """
        return self._join

    def getOrganizations(self):
        """Get the number of public organizations where the user is.

        Returns:
            int with the number of organizations

        """
        return self._organizations

    def getNumberOfRepositories(self):
        """Get the number of repositories of this user.

        Returns:
            int with the number of repositories
        """
        return self._numRepos

    def getBio(self):
        """Get the bio of the user.

        Returns:
            str with the bio
        """
        return self._bio

    def getPublicContributions(self):
        """Get only the public contributions of the user.

        Returns:
            int with the number of public contributions
        """
        return self._public

    def getPrivateContributions(self):
        """Get the number of private contributions of the user.

        Returns:
            int with the number of private contributions
        """
        return self._private

    # pylint: disable=R0201
    def isASCII(self, s):
        """Check if a string is ASCII."""
        return all(ord(c) < 128 for c in s)

    def getData(self):
        """Get data of a GitHub user."""
        url = self._server + self._name
        data = self._getDataFromURL(url)

        web = BeautifulSoup(data, "lxml")

        contributions_raw = web.find_all('h2',
                                         {'class': 'f4 text-normal mb-2'})

        contrText = contributions_raw[0].text
        contrText = contrText.lstrip().split(" ")[0]
        contrText = contrText.replace(",", "")
        self._contributions = int(contrText)

        # Avatar
        self._avatar = web.find("img", {"class": "avatar"})['src'][:-10]

        counters = web.find_all('span', {'class': 'counter'})

        # Number of repositories
        if 'k' not in counters[0].text:
            self._numRepos = int(counters[0].text)
        else:
            reposText = counters[0].text.replace(" ", "")
            reposText = reposText.replace("\n", "").replace("k", "")

            self._numRepos = int(reposText.split(".")[0]) * 1000 + \
                int(reposText.split(".")[1]) * 100

        # Followers
        if 'k' not in counters[2].text:
            self._followers = int(counters[2].text)
        else:
            follText = counters[2].text.replace(" ", "")
            follText = follText.replace("\n", "").replace("k", "")
            self._followers = int(follText.split(".")[0])*1000 + \
                int(follText.split(".")[1]) * 100

        # Location
        self._location = web.find("li", {"itemprop": "homeLocation"}).text

        # Date of creation
        join = web.findAll("a", {"class": "dropdown-item"})

        for j in join:
            if "Joined GitHub" in j.text:
                self._join = j["href"][-10:]

        # Bio
        bio = web.find_all("div", {"class": "user-profile-bio"})
        
        if bio:
            bio = bio[0].text
            if len(bio) > 0 and self.isASCII(bio):
                bioText = bio.replace("\n", "")
                bioText = bioText.replace("\t", " ").replace("\"", "")
                bioText = bioText.replace("\'", "")
                self._bio = bioText
            else:
                self._bio = ""

        # Number of organizations
        orgsElements = web.find_all("a", {"class": "avatar-group-item"})
        self._organizations = len(orgsElements)

    # pylint: disable=R0914
    def getRealContributions(self):
        """
        Get the real number of contributions.

        The real number of contibutions is: public and private contribs
        """
        datefrom = datetime.datetime.now() - relativedelta(days=366)
        dateto = datefrom + relativedelta(months=1) - relativedelta(days=1)
        private = 0

        while datefrom < datetime.datetime.now():
            fromstr = datefrom.strftime("%Y-%m-%d")
            tostr = dateto.strftime("%Y-%m-%d")
            url = "https://github.com/" + self._name
            url += "?tab=overview&from=" + fromstr + "&to=" + tostr

            data = self._getDataFromURL(url)
            web = BeautifulSoup(data, "lxml")

            contr = "f4 lh-condensed m-0 text-gray"
            pcontribs = web.find_all("span", {"class": contr})

            aux = web.find_all('span', {'class': 'text-gray m-0'})

            noContribs = False

            for compr in aux:
                if "had no activity during this period." in compr.text:
                    noContribs = True

            if not noContribs:
                for contrib in pcontribs:
                    contribution = None
                    contribution = contrib.text
                    contribution = contribution.lstrip().replace(",", "")
                    contribution = contribution.replace("\n", " ")
                    contribution = contribution.partition(" ")[0]
                    private += int(contribution)

            datefrom += relativedelta(months=1)
            dateto += relativedelta(months=1)

        self._private = private
        self._public = self._contributions - private

        if self._public < 0:  # Is not exact
            self._public = 0

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

        hdr = {'User-Agent': 'curl/7.43.0 (x86_64-ubuntu) \
        libcurl/7.43.0 OpenSSL/1.0.1k zlib/1.2.8 gh-rankings-grx',
               'Accept': 'text/html',
               'Pragma': 'no-cache',
               'Connection': 'keep-alive',
               'X-PJAX': 'true'}

        while code != 200:
            req = urllib.request.Request(url, headers=hdr)
            try:
                response = urllib.request.urlopen(req)
                code = response.code
                time.sleep(0.01)
            except HTTPError as e:
                code = e.code
                if code == 404:
                    break
            except URLError as e:
                time.sleep(3)
            except Exception as e:
                time.sleep(5)

        if code == 404:
            raise Exception("User was not found")
        return response.read().decode('utf-8')
