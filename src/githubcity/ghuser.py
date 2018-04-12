"""
Allows to get all data about a given GitHub user.

Author: Israel Blancas @iblancasa
Original idea: https://github.com/JJ/github-city-rankings
License:

The MIT License (MIT)
    Copyright (c) 2015-2017 Israel Blancas @iblancasa (http://iblancasa.com/)

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
from time import sleep
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup


class GitHubUser:
    """Manager of a GitHub User.

    Attributes:
        name (str): Name of the user (private).
        contributions (int): total contributions (web - last year) (private).
        public (int): public contributions in the last year (private).
        private (int): private contributions in the last year (private).
        followers (int): total number of followers of an user (private).
        numRepos (int): number of repositories of an user (private).
        organizations (int): number of public organizations (private).
        join (str): when the user joined. Format: %Y-%M-%D (private).
        avatar (str): URL where the user's avatar is (private).
        bio (str): bio of the user (private).
    """

    def __init__(self, name, server="https://github.com/"):
        """Constructor of the class.

        :param name: name (login) of an user in GitHub.
        :type name: str.
        :param server: server to query data. Default: https://github.com/
        :type server: str.
        """
        self.name = name
        self.server = server
        self.followers = -1
        self.numberOfRepos = -1
        self.organizations = -1
        self.contributions = -1
        self.join = ""
        self.avatar = ""
        self.bio = ""
        self.public = 0
        self.private = 0
        self.location = ""

    def export(self):
        """Export all attributes of the user to a dict.

        :return: attributes of the user.
        :rtype: dict.
        """
        data = {}
        data["name"] = self.name
        data["contributions"] = self.contributions
        data["avatar"] = self.avatar
        data["followers"] = self.followers
        data["join"] = self.join
        data["organizations"] = self.organizations
        data["repositories"] = self.numberOfRepos
        data["bio"] = self.bio
        data["private"] = self.private
        data["public"] = self.public
        data["location"] = self.location
        return data

    @staticmethod
    def isASCII(s):
        """Check if a string is ASCII.

        :param s: string to check if it is ASCII.
        :type s: str.
        :return: True if the string is ASCII.
        :rtype: boolean.
        """
        return all(ord(c) < 128 for c in s)

    def __getContributions(self, web):
        """Scrap the contributions from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        contributions_raw = web.find_all('h2',
                                         {'class': 'f4 text-normal mb-2'})
        try:
            contrText = contributions_raw[0].text
            contrText = contrText.lstrip().split(" ")[0]
            contrText = contrText.replace(",", "")
        except IndexError as error:
            print("There was an error with the user " + self.name)
            print(error)
        except AttributeError as error:
            print("There was an error with the user " + self.name)
            print(error)

        self.contributions = int(contrText)

    def __getAvatar(self, web):
        """Scrap the avatar from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        try:
            self.avatar = web.find("img", {"class": "avatar"})['src'][:-10]
        except IndexError as error:
            print("There was an error with the user " + self.name)
            print(error)
        except AttributeError as error:
            print("There was an error with the user " + self.name)
            print(error)

    def __getNumberOfRepositories(self, web):
        """Scrap the number of repositories from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        counters = web.find_all('span', {'class': 'Counter'})
        try:
            if 'k' not in counters[0].text:
                self.numberOfRepos = int(counters[0].text)
            else:
                reposText = counters[0].text.replace(" ", "")
                reposText = reposText.replace("\n", "").replace("k", "")

                if reposText and len(reposText) > 1:
                    self.numberOfRepos = int(reposText.split(".")[0]) * \
                        1000 + int(reposText.split(".")[1]) * 100
                elif reposText:
                    self.numberOfRepos = int(reposText.split(".")[0]) * 1000
        except IndexError as error:
            print("There was an error with the user " + self.name)
            print(error)
        except AttributeError as error:
            print("There was an error with the user " + self.name)
            print(error)

    def __getNumberOfFollowers(self, web):
        """Scrap the number of followers from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        counters = web.find_all('span', {'class': 'Counter'})
        try:
            if 'k' not in counters[2].text:
                self.followers = int(counters[2].text)
            else:
                follText = counters[2].text.replace(" ", "")
                follText = follText.replace("\n", "").replace("k", "")

                if follText and len(follText) > 1:
                    self.followers = int(follText.split(".")[0])*1000 + \
                        int(follText.split(".")[1]) * 100
                elif follText:
                    self.followers = int(follText.split(".")[0])*1000
        except IndexError as error:
            print("There was an error with the user " + self.name)
            print(error)
        except AttributeError as error:
            print("There was an error with the user " + self.name)
            print(error)

    def __getLocation(self, web):
        """Scrap the location from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        try:
            self.location = web.find("span", {"class": "p-label"}).text
        except AttributeError as error:
            print("There was an error with the user " + self.name)
            print(error)

    def __getJoin(self, web):
        """Scrap the join date from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        join = web.findAll("a", {"class": "dropdown-item"})
        for j in join:
            try:
                if "Joined GitHub" in j.text:
                    self.join = j["href"][-10:]
            except IndexError as error:
                print("There was an error with the user " + self.name)
                print(error)
            except AttributeError as error:
                print("There was an error with the user " + self.name)
                print(error)

    def __getBio(self, web):
        """Scrap the bio from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        bio = web.find_all("div", {"class": "user-profile-bio"})

        if bio:
            try:
                bio = bio[0].text
                if bio and GitHubUser.isASCII(bio):
                    bioText = bio.replace("\n", "")
                    bioText = bioText.replace("\t", " ").replace("\"", "")
                    bioText = bioText.replace("\'", "").replace("\\", "")
                    self.bio = bioText
                else:
                    self.bio = ""
            except IndexError as error:
                print("There was an error with the user " + self.name)
                print(error)
            except AttributeError as error:
                print("There was an error with the user " + self.name)
                print(error)

    def __getOrganizations(self, web):
        """Scrap the number of organizations from a GitHub profile.

        :param web: parsed web.
        :type web: BeautifulSoup node.
        """
        orgsElements = web.find_all("a", {"class": "avatar-group-item"})
        self.organizations = len(orgsElements)

    def getData(self):
        """Get data of the GitHub user."""
        url = self.server + self.name
        data = GitHubUser.__getDataFromURL(url)
        web = BeautifulSoup(data, "lxml")
        self.__getContributions(web)
        self.__getLocation(web)
        self.__getAvatar(web)
        self.__getNumberOfRepositories(web)
        self.__getNumberOfFollowers(web)
        self.__getBio(web)
        self.__getJoin(web)
        self.__getOrganizations(web)

    def getRealContributions(self):
        """Get the real number of contributions (private + public)."""
        datefrom = datetime.now() - relativedelta(days=366)
        dateto = datefrom + relativedelta(months=1) - relativedelta(days=1)
        private = 0

        while datefrom < datetime.now():
            fromstr = datefrom.strftime("%Y-%m-%d")
            tostr = dateto.strftime("%Y-%m-%d")
            url = self.server + self.name
            url += "?tab=overview&from=" + fromstr + "&to=" + tostr

            data = GitHubUser.__getDataFromURL(url)
            web = BeautifulSoup(data, "lxml")

            aux = "f4 lh-condensed m-0 text-gray"
            pcontribs = web.find_all("span", {"class": aux})

            aux = web.find_all('span', {'class': 'text-gray m-0'})

            noContribs = False

            for compr in aux:
                if "had no activity during this period." in compr.text:
                    noContribs = True

            try:
                if not noContribs:
                    for contrib in pcontribs:
                        contribution = None
                        contribution = contrib.text
                        contribution = contribution.lstrip().replace(",", "")
                        contribution = contribution.replace("\n", " ")
                        contribution = contribution.partition(" ")[0]
                        private += int(contribution)
            except IndexError as error:
                print("There was an error with the user " + self.name)
                print(error)
            except AttributeError as error:
                print("There was an error with the user " + self.name)
                print(error)

            datefrom += relativedelta(months=1)
            dateto += relativedelta(months=1)

        self.private = private
        self.public = self.contributions - private

        if self.public < 0:  # Is not exact
            self.public = 0

    @staticmethod
    def __getDataFromURL(url):
        """Read HTML data from an user GitHub profile.

        :param url: URL of the webpage to download.
        :type url: str.
        :return: webpage donwloaded.
        :rtype: str.
        """
        code = 0

        while code != 200:
            req = Request(url)
            try:
                response = urlopen(req)
                code = response.code
                sleep(0.01)
            except HTTPError as error:
                code = error.code
                if code == 404:
                    break
            except URLError as error:
                sleep(3)

        if code == 404:
            raise Exception("User was not found")
        return response.read().decode('utf-8')
