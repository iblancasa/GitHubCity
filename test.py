#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import sys, os
sys.path.append(os.getcwd())
from GitHubCity import *


class TestGitHubCity(unittest.TestCase):

    def test(self):
        ##########################TESTING KEYS#############
        #Testing GitHub ID
        idGH = os.environ.get('GH_ID')
        self.assertIsNotNone(idGH, "GitHub ID is None")
        self.assertIsInstance(idGH, str, "GitHub ID is not a str")
        self.assertNotEqual(idGH, "", "GitHub ID is an empty str")

        #Testing GitHub Secret
        secretGH = os.environ.get('GH_SECRET')
        self.assertIsNotNone(secretGH, "GitHub Secret is None")
        self.assertIsInstance(secretGH, str, "GitHub Secret is not a str")
        self.assertNotEqual(secretGH, "", "GitHub ID is an empty str")


        ##########################TESTING CLASS#############
        #Testing creation and initialization of the class
        cityA = GitHubCity("Granada",idGH,secretGH)
        self.assertIsNotNone(cityA, "City was not created")
        self.assertIsNotNone(cityA._city, "City name was not setting")
        self.assertIsNotNone(cityA._githubID, "GitHub ID was not setting")
        self.assertIsNotNone(cityA._githubSecret, "GitHub Secret was not setting")
        self.assertEqual(cityA._githubID,os.environ.get('GH_ID'), "GitHub ID was not setting correctly")
        self.assertEqual(cityA._githubSecret,os.environ.get('GH_SECRET'), "GitHub Secret was not setting correctly")
        self.assertNotEqual(cityA._city,"", "City name is an empy str")
        self.assertIsInstance(cityA._users,list,"Users list was not created")


        ##########################TESTING METHODS#############
        #Testing period calculation
        start = datetime.date(2015, 1, 1)
        finish = datetime.date(2015, 2, 1)
        start_result,final_result = cityA._getPeriod(start,finish)
        difference_dates = final_result-start_result
        difference_dates2 = start_result-start

        self.assertEqual(difference_dates.days,28, "Diference between "+str(final_result)+" and "+ \
                str(start_result)+" is incorrect")
        self.assertEqual(difference_dates2.days,32, "Diference between "+str(start_result)+" and "+ \
                str(start)+" is incorrect")
        self.assertEqual(start_result,finish+relativedelta(days=+1), "Finish date and start result \ date must be differenced in one day")


        #Testing URL composition
        url = cityA._getURL(1,start,finish)
        expected_url = "https://api.github.com/search/users?client_id="+\
        cityA._githubID+"&client_secret="+cityA._githubSecret+"&order=desc&q=sort:joined+"+\
        "type:user+location:Granada+created:2015-01-01..2015-02-01&per_page=100&page=1"

        self.assertIsNotNone(url,"URL was not returned")
        self.assertNotEqual(url,"","URL is an empty string")
        self.assertEqual(url,expected_url,
        "URL is not well formed")


        #Testing read API
        data = cityA._read_API(url)
        self.assertIsNotNone(data, "Data received from API is None")
        self.assertEqual(data["total_count"],16, "Total_count is not correct")
        self.assertEqual(len(data["items"]),16, "Items are not correct")


        #Testing add user
        added = cityA._addUsers(data["items"])
        self.assertIsNotNone(cityA._users, "Users in class is None")
        self.assertEqual(len(cityA._users),data["total_count"], "Users were not saved correctly")
        self.assertEqual(added,data["total_count"], "The number of users added is not correct")

        added = cityA._addUsers(data["items"])
        self.assertEqual(added,0, "The number of users added when all users are repeated is not correct")

        for i in data["items"]:
            self.assertEqual(cityA._users.count(i),1, "User "+str(i)+" is repeated")


        cityB = GitHubCity("Granada",idGH,secretGH)
        cityB._getPeriodUsers(start,finish)
        self.assertEqual(cityA._users,cityB._users, "Get period is not OK")

        #Testing getting all users from a city
        cityC = GitHubCity("Granada",idGH,secretGH)
        url_all = "https://api.github.com/search/users?client_id=" + \
        idGH + "&client_secret=" + secretGH + \
        "&q=type:user+location:Granada"

        data_all = cityC._read_API(url_all)

        cityC.getCityUsers()

        self.assertEqual(len(cityC._users),data_all["total_count"],"Total users was not calculated correctly")




if __name__ == '__main__':
    unittest.main()