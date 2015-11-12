#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib.request, os, datetime, time
from urllib.error import HTTPError
from dateutil.relativedelta import relativedelta

idGH = os.environ.get('GH_ID')
secretGH = os.environ.get('GH_SECRET')


city = "Barcelona"
users = []


def addUsers(new_users):
    global users
    global names
    repeat = 0
    for user in new_users:
        if not user["login"] in names:
            users.append(user)
            names.append(user["login"])
        else:
            repeat+=1
    return len(new_users)-repeat



def read_API(url):
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
            print(e.reason)
            print(e.code)
            print(e.read())
            print("Waiting...")
            time.sleep(60)
            code = e.code


    data = json.loads(response.read().decode('utf-8'))
    return data



def getURLBigs(page, start_date, final_date):
    url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
        "&order=desc&q=sort:joined+type:user+\
        location:"+city+\
        "created:"+start_date+".."+final_date+\
        "&per_page=100&page="+str(page)
    return url


def getPeriod(start, final):
    start = final
    start += datetime.timedelta(days=1)
    final = start + relativedelta(months=+1)
    return (start,final)


def getMonthUsers(start_date, final_date):
    url = getURLBigs(1,start_date,final_date)
    print(url)
    data = read_API(url)



    total_count = data["total_count"]
    addUsers(data['items'])

    if total_count>100:
        added = 0
        page = 1
        total_pages = int(total_count/100)+1

        while total_count>added:
            url = getURLBigs(page,start_date,final_date)
            print(url)
            data = read_API(url)
            page+=1

            if page==total_pages:
                page=1



            total_count = data["total_count"]
            added += addUsers(data['items'])




def getBigCityUsers():
    start_date = datetime.date(2008, 1, 1)
    final_date = datetime.date(2008, 2, 1)
    today = datetime.datetime.now().date()

    while start_date<today:
        getMonthUsers(start_date, final_date)
        start_date,final_date = getPeriod(start_date,final_date)
        print(str(start_date)+" -------- "+str(final_date))
        print("#####################################################################")



getBigCityUsers()
println(len(users))



