#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import urllib, json

idGH = os.environ.get('GH_ID')
secretGH = os.environ.get('GH_SECRET')


users = []
names = []

def getSizeCity(city):
    url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
        "&q=sort:followers+type:user+location:"+city

    response = urllib.urlopen(url)
    data = json.loads(response.read())
    return data['total_count']




def addUsers(new_users):
    global users
    global names
    for user in new_users:
        if not user["login"] in names:
            users.append(user)
            names.append(user["login"])



def read_API(url):
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    if "message" in data:
        print("API MESSAGE: "+data["message"])
        if "API rate limit exceeded for" in data["message"]:
            exit()
    return data



#Get All users from city
def getUsers(city):
    total_users=getSizeCity(city)
    page=1
    more=True
    global users


    if total_users<1000:
        while more:
            url = "https://api.github.com/search/users?client_id="+id+"&client_secret="+secret+ \
                "&q=type:user+location:"+city+"&per_page=100&page="+str(page)
            data = read_API(url)

            if len(data['items'])>0:
                addUsers(data['items'])
                page += 1
            else:
                more = False
    else:
        repos_limit = 999999999



        while len(users)<total_users:
            while more and page<=10:
                url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
                    "&q=sort:repositories+type:user+repos:<"+str(repos_limit)+"+location:"+city+"&per_page=100&page="+str(page)
                data = read_API(url)

                print(url)
                if len(data['items'])>0:
                    users+= data['items']
                    page += 1
                else:
                    more = False
                print("TOTAL USERS "+str(total_users))
                print("USUARIOS CONTADOS "+str(len(users)))

            print(len(users)<total_users)

            if len(users)<total_users:
                response = urllib.urlopen(users[len(users)-1]["repos_url"]+"?client_id="+idGH+"&client_secret="+secretGH)
                data = json.loads(response.read().decode('utf-8'))
                repos_limit=len(data)+1
                more=True
                page=1
        return users




users=getUsers("Barcelona")
print(len(users))



