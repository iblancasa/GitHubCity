#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import urllib, json

id = os.environ.get('GH_ID')
secret = os.environ.get('GH_SECRET')

users = []
city = "Granada"

page = 1
more = True

while more:
    url = "https://api.github.com/search/users?client_id="+id+"&client_secret="+secret+ \
        "&q=sort:followers+type:user+location:"+city+"&per_page=100&page="+str(page)

    response = urllib.urlopen(url)
    data = json.loads(response.read())
    if len(data['items'])>0:
        users = users + data['items']
        page = page + 1
    else:
        more = False



print len(users)
