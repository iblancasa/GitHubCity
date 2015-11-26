# GitHubCity

[![Build Status](https://travis-ci.org/iblancasa/GitHubCity.svg?branch=master)](https://travis-ci.org/iblancasa/GitHubCity)
[![GitHub license](https://img.shields.io/github/license/iblancasa/GitHubCity.svg)](https://github.com/iblancasa/GitHubCity)[![Coverage Status](https://coveralls.io/repos/iblancasa/GitHubCity/badge.svg?branch=testing&service=github)](https://coveralls.io/github/iblancasa/GitHubCity?branch=testing)

## What is this?
This is a small library which gets all GitHub users given a city. Original idea is [Top-GitHub-Users-Data](https://github.com/JJ/top-github-users-data) by [@JJ](https://github.com/JJ), an adaptation of [top-github-users](https://github.com/paulmillr/top-github-users) from [@paulmillr](https://github.com/paulmillr/).

## What I can do with this?
Now, you only can get all user names from a city (with a city in the location field). In future, this will be an amazing library.

## What I need to run this?
You will need to install Python 3. Python 2 is not supported. I recommend you [install Anaconda](https://www.continuum.io/).

In addition, you will need to get ID and Secret from a GitHub application. [You can register your own application here!](https://github.com/settings/applications/new).

#### Dependences
You have a ``requeriments.txt`` file. Install all dependences with ``pip install -r requeriments.txt``.


## Getting started
#### Basic example
```python
nameCity = "Granada"
GitHubID = "asdadfs5ds8sdfsdf8c"
GitHubSecret = "asdad45asfsdf8vdfg8sdfgv"

city = GitHubCity(nameCity,GitHubID,GitHubSecret)
city.getCityUsers()
```

#### Excluding users
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

When you read this file and parse it to JSON, you can add it to the class in constructor:
```python
GitHubCity(nameCity,GitHubID,GitHubSecret, jsonData)
```

### The MIT License (MIT)
    Copyright (c) 2015 Israel Blancas @iblancasa (http://iblancasa.com/)

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
