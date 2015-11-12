#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,  json, time
import urllib.request
from urllib.error import HTTPError

idGH = os.environ.get('GH_ID')
secretGH = os.environ.get('GH_SECRET')


users = []
names = []

def getSizeCity(city):
    url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
        "&q=repos:1..999999999+type:user+location:"+city
    data = read_API(url)
    return data['total_count']


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


def getURL(page,order,city,repositorieslim):
        url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
            "&order="+order+"&q=sort:repositories+type:user+repos:"+repositorieslim+"+location:"+city+"&per_page=100&page="+str(page)
        return url


def getURLZero(page,order,city):
        url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
            "&order="+order+"&q=sort:joined+type:user+repos:"+repositorieslim+"+location:"+city+"&per_page=100&page="+str(page)


def getsize0users(city):
    url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
        "&q=repos:0+type:user+location:"+city
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    return data['total_count']



#Get All users from city
def getUsers(city):
    total_users=getSizeCity(city)
    size0users=getsize0users(city)
    print(size0users)
    zerobig = size0users>1000
    print(size0users+total_users)
    page=1
    more=True
    repos_limit = 999999999

    if zerobig:
        min_repos="1"
        print(str(total_users)+" users with more than 0 repos")
    else:
        min_repos="0"
        print(str(total_users)+" users")



    while len(users)<total_users:
        while more and page<=10 and len(users)<total_users:
            url = getURL(page,"desc",city,min_repos+".."+str(repos_limit))
            data = read_API(url)

            print(url)
            if "items" in data and len(data['items'])>0:
                repeat = addUsers(data['items'])
                if repeat != len(data['items']) and repeat != 0 and page!=1:
                    page -= 2
                    if page < 1:
                        page = 1
                else:
                    page +=1
                print("Tengo --> "+str(len(users))+"   Quiero llegar a -->"+str(total_users))

            else:
                more = False


        if repos_limit==1:
            repos_limit = 999999999

        if len(users)<total_users and "items" in data:
            if len(data['items'])==0:
                page-=1
                url = getURL(page,"desc",city,min_repos+".."+str(repos_limit))
                data = read_API(url)

            URL_reposuser=data['items'][len(data['items'])-1]["repos_url"]+\
                "?client_id="+idGH+"&client_secret="+secretGH

            response = urllib.request.urlopen(URL_reposuser)
            data = json.loads(response.read().decode('utf-8'))
            repos_limit=len(data)
            more=True
            page=1

    if zerobig:
        print("Calculating 0 users")
        order ="desc"
        added = 0
        old_size = len(users)

        total_users+=size0users
        page = 1
        print(total_users)
        print(total_users<len(users))
        print(len(users))


        while total_users>len(users):
            while added<1000:



                url = getURL(page,order,city,"0")
                data = read_API(url)
                print(url)
                if "items" in data and len(data['items'])>0:
                    old_size = len(users)
                    repeat = addUsers(data['items'])
                    added += len(users)-old_size

                    print("Tengo --> "+str(len(users))+"   Quiero llegar a -->"+str(total_users))
                    print("Añadidos --> "+str(added)+"  hasta "+str(size0users))

                    if repeat != len(data['items']) and repeat != 0 and page!=1:
                        page -= 2
                        if page < 1:
                            page = 1
                    else:
                        page +=1
                        if page==11:
                            page=1

                if total_users==len(users):
                    print(total_users)
                    return
            if order=="desc":
                order="asc"
            else:
                order="desc"
            added = 0
        print("salgo de la función")






getUsers("Barcelona")

print(len(users))

