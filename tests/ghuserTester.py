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
import sys
import os
import unittest
import httpretty
from bs4 import BeautifulSoup
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), 'src'))
print(os.path.join(os.path.dirname(sys.path[0]), 'src'))
from githubcity.ghuser import GitHubUser


class ghcityTester(unittest.TestCase):
    """Tester of the class GitHubUser."""

    def test_init(self):
        """Test the creation of the class with its configuration."""
        pass

    def test_getNumberOfRepos(self):
        """Test the private method getNumberOfRepos."""
        # Given
        data = ""
        with open("tests/resources/user.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("iblancasa")
        user._GitHubUser__getNumberOfRepositories(web)
        # Then
        self.assertEqual(user.numberOfRepos, 141)

    def test_getNumberOfReposK(self):
        """Test the private method getNumberOfRepos for k repositories.

        This happens when the number of repositories is more than 1000.
        """
        # Given
        data = ""
        with open("tests/resources/userk.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("vim-scripts")
        user._GitHubUser__getNumberOfRepositories(web)
        # Then
        self.assertEqual(user.numberOfRepos, 5200)

    def test_getNumberOfFollowers(self):
        """Test the private method getNumberOfFollowers."""
        # Given
        data = ""
        with open("tests/resources/user.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("iblancasa")
        user._GitHubUser__getNumberOfFollowers(web)
        # Then
        self.assertEqual(user.followers, 107)

    def test_getNumberOfFollowersk(self):
        """Test the private method getNumberOfFollowers for k followers.

        This happens when the number of followers is more than 1000."""
        # Given
        data = ""
        with open("tests/resources/userk.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("vim-scripts")
        user._GitHubUser__getNumberOfFollowers(web)
        # Then
        self.assertEqual(user.followers, 3800)

    def test__getContributions(self):
        """Test the private method getContributions."""
        # Given
        data = ""
        with open("tests/resources/user.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("iblancasa")
        user._GitHubUser__getContributions(web)
        # Then
        self.assertEqual(user.contributions, 490)

    def test__getAvatar(self):
        """Test the private method getAvatar."""
        # Given
        data = ""
        with open("tests/resources/user.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("iblancasa")
        user._GitHubUser__getAvatar(web)
        # Then
        self.assertEqual(user.avatar,
                         "https://avatars0.githubusercontent.com/u/4806311")

    def test__getLocation(self):
        """Test the private method getLocation."""
        # Given
        data = ""
        with open("tests/resources/user.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("iblancasa")
        user._GitHubUser__getLocation(web)
        # Then
        self.assertEqual(user.location, "Granada, Andalucía, Spain")

    def test__getBio(self):
        """Test the private method getBio."""
        # Given
        data = ""
        with open("tests/resources/user.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("iblancasa")
        user._GitHubUser__getBio(web)
        # Then
        self.assertEqual(user.bio, "This is my bio.")

    def test__getOrganizations(self):
        """Test the private method getOrganizations."""
        # Given
        data = ""
        with open("tests/resources/user.html") as userWeb:
            data = userWeb.read()
        web = BeautifulSoup(data, "lxml")
        # When
        user = GitHubUser("iblancasa")
        user._GitHubUser__getOrganizations(web)
        # Then
        self.assertEqual(user.organizations, 7)

    def test_export(self):
        # Given
        user = GitHubUser("iblancasa")
        user.numberOfRepos = 141
        user.bio = ""
        user.private = 0
        user.public = 0
        user.location = 'Granada, Andalucía, Spain'
        user.contributions = 490
        user.name = "iblancasa"
        user.join = "2013-06-24"
        user.followers = 107
        user.organizations = 7
        user.avatar = "https://avatars0.githubusercontent.com/u/4806311"
        # When
        exportedUser = {'name': 'iblancasa',
                        'bio': '',
                        'join': '2013-06-24',
                        'organizations': 7,
                        'private': 0,
                        'contributions':490,
                        'public': 0,
                        'location': 'Granada, Andalucía, Spain',
                        'avatar':
                            'https://avatars0.githubusercontent.com/u/4806311',
                        'repositories': 141,
                        'followers': 107
                        }
        # Then
        self.assertEqual(user.export(), exportedUser)

    def test_getData(self):
        # Given
        with open("tests/resources/user.html") as userWeb:
            reply = userWeb.read()
        httpretty.enable()
        httpretty.register_uri(httpretty.GET, "https://github.com/iblancasa",
                               body=reply,
                               content_type="text/html")
        # When
        user = GitHubUser("iblancasa")
        user.getData()
        # Then
        self.assertEqual(user.numberOfRepos, 141)
        self.assertEqual(user.bio, "This is my bio.")
        self.assertEqual(user.private, 0)
        self.assertEqual(user.public, 0)
        self.assertEqual(user.contributions, 490)
        self.assertEqual(user.name, "iblancasa")
        self.assertEqual(user.join, "2013-06-24")
        self.assertEqual(user.followers, 107)
        self.assertEqual(user.organizations, 7)
        self.assertEqual(user.avatar,
                         "https://avatars0.githubusercontent.com/u/4806311")

if __name__ == "__main__":
    unittest.main()
