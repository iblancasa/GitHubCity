#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,  json, time
import urllib.request

idGH = os.environ.get('GH_ID')
secretGH = os.environ.get('GH_SECRET')


users = []
names = []

def getSizeCity(city):
    url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
        "&q=repos:1..999999999+type:user+location:"+city
    print("size   "+url)
    response = urllib.request.urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
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
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
    code = 0

    while code !=200:
        req = urllib.request.Request(url,headers=hdr)

        response = urllib.request.urlopen(req)
        code = response.code
        print("Server says: "+str(code))

    data = json.loads(response.read().decode('utf-8'))

    if "message" in data:
        print("API MESSAGE: "+data["message"])
        while "message" in data:
            print("Waiting 30 seconds...")
            time.sleep(30)
            response = urllib.urlopen(url)
            data = json.loads(response.read())

    return data


def getURL(page,order,city,repositorieslim):
        url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
            "&order="+order+"&q=sort:repositories+type:user+repos:"+repositorieslim+"+location:"+city+"&per_page=100&page="+str(page)
        return url



def getZeroUsers(city):
    order="asc"
    while more and page<=10:
        url = getURL(page,order,city,"0")
        data = read_API(url)

        print(url)
        if "items" in data and len(data['items'])>0:
            repeat = addUsers(data['items'])
            print("REPETIDOS "+str(repeat))
            if repeat != len(data['items']) and repeat != 0 and page!=1:
                page = 1
            else:
                page +=1

        elif order=="asc":
            order="desc"
        else:
            more = False
        print("TOTAL USERS "+str(total_users))
        print("USUARIOS CONTADOS "+str(len(users)))




#Get All users from city
def getUsers(city):
    total_users=getSizeCity(city)
    page=1
    more=True
    global names


    if total_users<1000:
        '''
        while more:
            url = "https://api.github.com/search/users?client_id="+id+"&client_secret="+secret+ \
                "&q=type:user+location:"+city+"&per_page=100&page="+str(page)
            data = read_API(url)

            if len(data['items'])>0:
                addUsers(data['items'])
                page += 1
            else:
                more = False
        '''
    else:
        repos_limit = 999999999

        while len(users)<total_users:
            while more and page<=10:
                url = getURL(page,"desc",city,"1.."+str(repos_limit))
                data = read_API(url)

                print(url)
                if "items" in data and len(data['items'])>0:
                    repeat = addUsers(data['items'])
                    print("REPETIDOS "+str(repeat))
                    if repeat != len(data['items']) and repeat != 0 and page!=1:
                        page = 1
                    else:
                        page +=1

                else:
                    more = False
                print("TOTAL USERS "+str(total_users))
                print("USUARIOS CONTADOS "+str(len(users)))

            if repos_limit==1:
                #getZeroUsers()
                return

            if len(users)<total_users:
                URL_reposuser=data['items'][len(data['items'])-1]["repos_url"]+\
                    "?client_id="+idGH+"&client_secret="+secretGH

                response = urllib.urlopen(URL_reposuser)
                data = json.loads(response.read().decode('utf-8'))
                repos_limit=len(data)
                more=True
                page=1






users=getUsers("Barcelona")
print(len(users))

