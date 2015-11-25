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

import unittest
import sys
import os
import json
sys.path.append(os.getcwd())
from GitHubCity import *


class TestGitHubCity(unittest.TestCase):

    def test(self):
        ##########################TESTING KEYS#############
        # Testing GitHub ID
        print("Testing keys")

        idGH = os.environ.get('GH_ID')
        self.assertIsNotNone(idGH, "GitHub ID is None")
        self.assertIsInstance(idGH, str, "GitHub ID is not a str")
        self.assertNotEqual(idGH, "", "GitHub ID is an empty str")

        # Testing GitHub Secret
        secretGH = os.environ.get('GH_SECRET')
        self.assertIsNotNone(secretGH, "GitHub Secret is None")
        self.assertIsInstance(secretGH, str, "GitHub Secret is not a str")
        self.assertNotEqual(secretGH, "", "GitHub ID is an empty str")

        print("Testing keys: OK")

        ##########################TESTING CLASS#############
        # Testing creation and initialization of the class
        print("Testing class")

        cityA = GitHubCity("Granada", idGH, secretGH)
        self.assertIsNotNone(cityA, "City was not created")
        self.assertIsNotNone(cityA._city, "City name was not setting")
        self.assertIsNotNone(cityA._githubID, "GitHub ID was not setting")
        self.assertIsNotNone(cityA._githubSecret,
                             "GitHub Secret was not setting")
        self.assertEqual(cityA._githubID, os.environ.get(
            'GH_ID'), "GitHub ID was not setting correctly")
        self.assertEqual(cityA._githubSecret, os.environ.get(
            'GH_SECRET'), "GitHub Secret was not setting correctly")
        self.assertNotEqual(cityA._city, "", "City name is an empy str")
        self.assertIsInstance(
            cityA._names, set, "Users list names was not created")

        print("Testing class: OK")

        ##########################TESTING METHODS#############
        # Testing period calculation
        print("Testing methods")
        print("Period calculation")
        start = datetime.date(2015, 1, 1)
        finish = datetime.date(2015, 2, 1)
        start_result, final_result = cityA._getPeriod(start, finish)
        difference_dates = final_result - start_result
        difference_dates2 = start_result - start

        self.assertEqual(difference_dates.days, 28, "Diference between " + str(final_result) + " and " +
                         str(start_result) + " is incorrect")
        self.assertEqual(difference_dates2.days, 32, "Diference between " + str(start_result) + " and " +
                         str(start) + " is incorrect")
        self.assertEqual(start_result, finish + relativedelta(days=+1),
                         "Finish date and start result \ date must be differenced in one day")

        # Testing URL composition
        print("URL Composition")
        url = cityA._getURL(1, start, finish)
        expected_url = "https://api.github.com/search/users?client_id=" +\
            cityA._githubID + "&client_secret=" + cityA._githubSecret + "&order=desc&q=sort:joined+" +\
            "type:user+location:Granada+created:2015-01-01..2015-02-01&per_page=100&page=1"

        self.assertIsNotNone(url, "URL was not returned")
        self.assertNotEqual(url, "", "URL is an empty string")
        self.assertEqual(url, expected_url,
                         "URL is not well formed")

        # Testing read API
        print("Read API")
        data = cityA._read_API(url)
        self.assertIsNotNone(data, "Data received from API is None")
        self.assertEqual(data["total_count"], 16, "Total_count is not correct")
        self.assertEqual(len(data["items"]), 16, "Items are not correct")

        # Testing add user
        print("Add user")
        added = cityA._addUsers(data["items"])
        self.assertIsNotNone(cityA._names, "Users in class is None")
        self.assertEqual(len(cityA._names), data[
                         "total_count"], "Users were not saved correctly")
        self.assertEqual(added, data["total_count"],
                         "The number of users added is not correct")

        added = cityA._addUsers(data["items"])
        self.assertEqual(
            added, 0, "The number of users added when all users are repeated is not correct")

        cityB = GitHubCity("Granada", idGH, secretGH)
        cityB._getPeriodUsers(start, finish)
        self.assertEqual(cityA._names, cityB._names, "Get period is not OK")

        # Testing getting all users from a city
        print("Getting all users from a city")
        cityC = GitHubCity("Granada", idGH, secretGH)
        url_all = "https://api.github.com/search/users?client_id=" + \
            idGH + "&client_secret=" + secretGH + \
            "&q=type:user+location:Granada"

        data_all = cityC._read_API(url_all)
        cityC.getCityUsers()
        self.assertEqual(len(cityC._names), data_all[
                         "total_count"], "Total users was not calculated correctly")

        # Texting exclude users
        print("Exclude users")
        dataExclude = [
            {
                "login": "asdpokjdf",
                "id": 99999,
                "avatar_url": "https://avatars.githubusercontent.com/u/99999?v=3",
                "gravatar_id": "",
                "url": "https://api.github.com/users/asdpokjdf",
                "html_url": "https://github.com/asdpokjdf",
                "followers_url": "https://api.github.com/users/asdpokjdf/followers",
                "following_url": "https://api.github.com/users/asdpokjdf/following{/other_user}",
                "gists_url": "https://api.github.com/users/asdpokjdf/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/asdpokjdf/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/asdpokjdf/subscriptions",
                "organizations_url": "https://api.github.com/users/asdpokjdf/orgs",
                "repos_url": "https://api.github.com/users/asdpokjdf/repos",
                "events_url": "https://api.github.com/users/asdpokjdf/events{/privacy}",
                "received_events_url": "https://api.github.com/users/asdpokjdf/received_events",
                "type": "User",
                "site_admin": "false",
                "score": 1.0
            },
            {
                "login": "testingperson",
                "id": 999999999,
                "avatar_url": "https://avatars.githubusercontent.com/u/999999999?v=3",
                "gravatar_id": "",
                "url": "https://api.github.com/users/testingperson",
                "html_url": "https://github.com/testingperson",
                "followers_url": "https://api.github.com/users/testingperson/followers",
                "following_url": "https://api.github.com/users/testingperson/following{/other_user}",
                "gists_url": "https://api.github.com/users/testingperson/gists{/gist_id}",
                "starred_url": "https://api.github.com/users/testingperson/starred{/owner}{/repo}",
                "subscriptions_url": "https://api.github.com/users/testingpersontestingperson/subscriptions",
                "organizations_url": "https://api.github.com/users/testingperson/orgs",
                "repos_url": "https://api.github.com/users/testingperson/repos",
                "events_url": "https://api.github.com/users/testingperson/events{/privacy}",
                "received_events_url": "https://api.github.com/users/testingperson/received_events",
                "type": "User",
                "site_admin": "false",
                "score": 1.0
            }]

        fileJSON = open('testExclude.json')
        excluded = json.loads(fileJSON.read())
        fileJSON.close()
        cityD = GitHubCity("Granada", idGH, secretGH, excluded)
        cityD._addUsers(dataExclude)

        self.assertIn("testingperson", cityD._names,
                      "Add new user was no completed correctly when there is an excluded list")
        self.assertNotIn("asdpokjdf", cityD._names,
                         "User was added to the users list and he is in excluded list")
        print("Testing methods: OK")

if __name__ == '__main__':
    unittest.main()
