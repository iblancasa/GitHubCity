#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, os, datetime, time, json
from urllib.error import HTTPError
from dateutil.relativedelta import relativedelta


class GitHubCity:
    def __init__(self,city, githubID, githubSecret):
        self._city = city
        self._users = []
        self._githubID = githubID
        self._githubSecret = githubSecret

    def _addUsers(self, new_users):
        repeat = 0
        for user in new_users:
            if not user["login"] in self._names:
                self._users.append(user)
                self._names.append(user["login"])
            else:
                repeat+=1
        return len(new_users)-repeat



    def _read_API(self, url):
        code = 0
        hdr = {'User-Agent': 'curl/7.43.0 (x86_64-ubuntu) libcurl/7.43.0 OpenSSL/1.0.1k zlib/1.2.8 gh-rankings-grx',
        'Accept': 'application/vnd.github.v3.text-match+json'
        }
        while code !=200:
            req = urllib.request.Request(url,headers=hdr)
            try:
                response = urllib.request.urlopen(req)
                code = response.code
            except urllib.error.URLError as e:
                time.sleep(60)
                code = e.code

        data = json.loads(response.read().decode('utf-8'))
        return data



    def _getURL(self, page, start_date, final_date):
        url = "https://api.github.com/search/users?client_id="+self._githubID+"&client_secret="+self._githubSecret+ \
            "&order=desc&q=sort:joined+type:user+location:"+self._city+ \
            "+created:"+start_date.strftime("%Y-%m-%d")+\
            ".."+final_date.strftime("%Y-%m-%d")+\
            "&per_page=100&page="+str(page)
        return url


    def _getPeriod(self, start, final):
        start = final + relativedelta(days=+1)
        final = start + relativedelta(months=+1)
        return (start,final)


    def _getMonthUsers(self, start_date, final_date):
        url = self._getURL(1,start_date,final_date)
        data = self._read_API(url)

        total_count = data["total_count"]
        added = self._addUsers(data['items'])

        page = 1
        total_pages = int(total_count/100)+1

        while total_count>added:
            page+=1
            if page>total_pages:
                page=1

            url = self._getURL(page,start_date,final_date)

            data = _read_API(url)

            total_count = data["total_count"]
            added += self._addUsers(data['items'])




    def getCityUsers(self):
        self._names = []
        start_date = datetime.date(2008, 1, 1)
        final_date = datetime.date(2008, 2, 1)
        today = datetime.datetime.now().date()

        while start_date<today:
            self._getMonthUsers(start_date, final_date)
            start_date,final_date = self._getPeriod(start_date,final_date)

    def getTotalUsers(self):
        if len(self._users)==0:
            self.getCityUsers()

        return len(self._users)

###
#idGH = os.environ.get('GH_ID')
#secretGH = os.environ.get('GH_SECRET')
#granada = GitHubCity("Granada", idGH, secretGH)
#print(granada.getTotalUsers())
###
