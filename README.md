# GitHubCity

[![Build Status](https://travis-ci.org/iblancasa/GitHubCity.svg?branch=master)](https://travis-ci.org/iblancasa/GitHubCity)
[![GitHub license](https://img.shields.io/github/license/iblancasa/GitHubCity.svg)](https://github.com/iblancasa/GitHubCity)[![Coverage Status](https://coveralls.io/repos/iblancasa/GitHubCity/badge.svg?branch=master&service=github)](https://coveralls.io/github/iblancasa/GitHubCity?branch=master)
[![Known Vulnerabilities](https://snyk.io/test/github/iblancasa/githubcity/badge.svg)](https://snyk.io/test/github/iblancasa/githubcity)
[![Dependency Status](https://gemnasium.com/badges/github.com/iblancasa/GitHubCity.svg)](https://gemnasium.com/github.com/iblancasa/GitHubCity)

## What is this?

This is a small library which gets all GitHub users given a city. Original idea is [Top-GitHub-Users-Data](https://github.com/JJ/top-github-users-data) by [@JJ](https://github.com/JJ), an adaptation of [top-github-users](https://github.com/paulmillr/top-github-users) from [@paulmillr](https://github.com/paulmillr/).

## What I can do with this?

This is an amazing Python library to study the GitHub community in a
location. You can get all the GitHub users from a given location and
obtain some data. For instance, you can generate one ranking
like
[this ranking with the users from Spain (and its provinces)](https://github.com/iblancasa/GitHubRankingsSpain). 

## What I need to run this?

You will need to install Python 3. *Python 2 is not supported*.

In addition, you will need to get an ID and Secret for a GitHub
application, [after registering your own application here!](https://github.com/settings/applications/new).

### Dependencies

There is a ``requirements.txt`` file included in this repo. Install all dependences with ``pip install -r requirements.txt``.

## How to install

There are two options to install this library and its dependencies.

### Install from the source code

You need to clone (or download) this repository. Then, go to ``src`` folder and run:
```shell
python setup.py install
```

### Install from pip

[This library is available to be installed using pip.](https://pypi.python.org/pypi?:action=display&name=githubcity)

```shell
pip install githubcity
```


## Getting started

[You can see one example about how to use this library here](https://github.com/iblancasa/GitHubSpanishRankingGenerator).

### Basic example

```python
idGH = os.environ.get('GH_ID')
secretGH = os.environ.get('GH_SECRET')
configuration = {
   "excludedLocations": [],
   "excludedUsers": [],
   "intervals": [
       [
           "2008-01-01",
           "2015-12-30"
       ]
   ],
   "last_date": "2015-12-30",
   "locations": [
       "Ceuta"
       ],
   "name": "Ceuta"
       }
ciudad = GitHubCity(idGH, secretGH, configuration)
ciudad.calculateBestIntervals()
ciudad.addFilter("repos", ">1")
ciudad.addFilter("followers", ">1")
ciudad.getCityUsers()
```

### Excluding users

You can generate a JSON file like this (each element is an user and this properties are name -login name of the user- and reason -why this user has been banned-):

```json
[
  {
    "name": "asdpokjdf",
    "reason": "It is only a test"
  },
  {
    "name": "asdfasdf",
    "reason": "It is only a test"
  },
  {
    "name": "asdfasdfadf",
    "reason": "It is only a test"
  }
]
```


## The MIT License (MIT)
    Copyright (c) 2015-2017 Israel Blancas @iblancasa (http://iblancasa.com/)

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
