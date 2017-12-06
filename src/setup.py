"""Allows to get all data about a given GitHub City.

This module allow to developers to get all users of GitHub that have a
given city in their profile. For example, if I want getting all users
from London,. I will get all users that have London in their
profiles (they could live in London or not)

Author: Israel Blancas @iblancasa
Original idea: https://github.com/JJ/github-city-rankings
License:

The MIT License (MIT)
    Copyright (c) 2015-2017 Israel Blancas @iblancasa (http://iblancasa.com/)

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the Software), to deal in the Software
    without restriction, including without
    limitation the rights to use, copy, modify, merge,
    publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED AS IS, WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
    PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
    USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from setuptools import setup
setup(
    name='githubcity',
    version='1.0.4',
    description='GitHub city ranking creator',
    author='Israel Blancas @iblancasa',
    author_email='iblancasa@gmail.com',
    url='https://github.com/iblancasa/GitHubCity',
    download_url='https://github.com/iblancasa/GitHubCity/tarball/0.01',
    keywords=['github', 'ranking', 'data', 'api'],
    classifiers=[],
    install_requires=[
        'python-dateutil==2.4.2',
        'beautifulsoup4==4.6.0',
        'lxml==4.1.1',
        'coloredlogs==5.0',
        'pystache==0.5.4',
        'httpretty==0.8.14'
    ],
    packages=['githubcity'],
    py_modules=["githubcity"],
    long_description=open('../README.md').read(),
    license='MIT'
)
