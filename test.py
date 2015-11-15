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
        cityA = GitHubCity("Ceuta",idGH,secretGH)
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
        start = datetime.date(2010, 1, 1)
        finish = datetime.date(2010, 2, 1)
        start_result,final_result = cityA._getPeriod(start,finish)
        difference_dates = final_result-start_result
        difference_dates2 = start_result-start

        self.assertEqual(difference_dates.days,28, "Diference between "+str(final_result)+" and "+str(start_result)+" is incorrect")
        self.assertEqual(difference_dates2.days,32, "Diference between "+str(start_result)+" and "+str(start)+" is incorrect")
        self.assertEqual(start_result,finish+relativedelta(days=+1), "Finish date and start result date must be differenced in one day")



if __name__ == '__main__':
    unittest.main()



#
#idGH = os.environ.get('GH_ID')
#secretGH = os.environ.get('GH_SECRET')
#granada = GitHubCity("Ceuta", idGH, secretGH)
#print(granada.getTotalUsers())