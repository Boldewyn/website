# -*- coding: UTF-8 -*-

from distutils.core import setup
from website import get_version

setup(
    name = 'website',
    packages = ['website'],
    version = get_version(),
    author = 'Manuel Strehl',
    author_email = 'boldewyn [at] googlemail.com',
    url = 'http://boldewyn.github.com/website/',
    description = 'HTML to HTML transformer',
    #    long_description = u'''
    #website generates web sites from a bunch of HTML files. Great! Let\u2019s look at it.
    #
    #::
    #
    #  $ ls
    #  _articles/
    #  _config.py
    #  _templates/
    #  assets/
    #  $ ls _articles
    #  _articles/my_post.html
    #  $ cat _articles/my_post.html
    #  Title: My First Post
    #  Date: 2011-07-01
    #  Subject: blog, Python, simple, usable
    #
    #  <p>This is my first post.</p>
    #  <ul><li>Look! A list!</li></ul>
    #
    #In steps website to produce from this a fully functional web site. Run it on
    #this folder and see the magic happen.
    #
    #::
    #
    #  $ python -m website.__main__
    #  $ ls
    #  _articles/
    #  _config.py
    #  _templates/
    #  assets/
    #  site/
    #  $ ls site
    #  site/assets/
    #  site/my_post.html
    #  $ cat site/my_post.html
    #  <!DOCTYPE html>
    #  <html lang="en">
    #    <head>
    #      <title>My First Post</title>
    #  [\u2026]
    #  <p>This is my first post.</p>
    #  <ul><li>Look! A list!</li></ul>
    #  [\u2026]
    #
    #The new folder site/ contains the finished data, complete with index files,
    #news feeds and assets. It\u2019s ready to get uploaded or viewed directly.'''.encode("UTF-8"),
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: PHP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
    ],
    requires = ["BeautifulSoup", "Babel", "Mako"]
)
