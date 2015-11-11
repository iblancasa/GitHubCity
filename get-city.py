#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, urllib, json, time

idGH = os.environ.get('GH_ID')
secretGH = os.environ.get('GH_SECRET')


users = []
names = []

def getSizeCity(city):
    url = "https://api.github.com/search/users?client_id="+idGH+"&client_secret="+secretGH+ \
        "&q=repos:1..999999999+type:user+location:"+city
    print("size   "+url)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
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
    response = urllib.urlopen(url)
    data = json.loads(response.read())

    if "message" in data:
        print("API MESSAGE: "+data["message"])
        while "message" in data:
            print("Waiting 30 seconds...")
            time.sleep(30)
            response = urllib.urlopen(url)
            data = json.loads(response.read())

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
                    "&q=sort:repositories+type:user+repos:1.."+str(repos_limit)+"+location:"+city+"&per_page=100&page="+str(page)
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

            if len(users)<total_users:
                response = urllib.urlopen(data['items'][len(data['items'])-1]["repos_url"]+"?client_id="+idGH+"&client_secret="+secretGH)
                data = json.loads(response.read().decode('utf-8'))
                repos_limit=len(data)
                more=True
                page=1

            if repos_limit==1:
                #




users=getUsers("Barcelona")
print(len(users))

target = open("nombre", 'w')
for i in users:
    target.write(i)
    target.write("\n")
target.close()
