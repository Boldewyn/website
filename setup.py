# -*- coding: UTF-8 -*-

import os
from distutils.core import setup
from website import get_version


data_files = []
for dirpath, dirnames, filenames in os.walk("website"):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if filenames:
        ls = [os.path.join(dirpath, f) for f in filenames if not f.endswith(".pyc") and not f.endswith(".py")]
        if len(ls):
            data_files.append((dirpath, ls))


setup(
    name = 'website',
    packages = ['website', 'website._webtools'],
    version = get_version(),
    author = 'Manuel Strehl',
    author_email = 'boldewyn [at] googlemail.com',
    url = 'http://boldewyn.github.com/website/',
    description = 'HTML to HTML transformer',
    long_description = '''website generates web sites from a bunch of HTML files. Great! Let's look at it.

::

  $ ls
  _articles/
  _config.py
  _templates/
  assets/
  $ ls _articles
  _articles/my_post.html
  $ cat _articles/my_post.html
  Title: My First Post
  Date: 2011-07-01
  Subject: blog, Python, simple, usable

  <p>This is my first post.</p>
  <ul><li>Look! A list!</li></ul>

In steps website to produce from this a fully functional web site. Run it on
this folder and see the magic happen.

::

  $ python -m website.__main__
  $ ls
  _articles/
  _config.py
  _templates/
  assets/
  site/
  $ ls site
  site/assets/
  site/my_post.html
  $ cat site/my_post.html
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <title>My First Post</title>
  [...]
  <p>This is my first post.</p>
  <ul><li>Look! A list!</li></ul>
  [...]

The new folder site/ contains the finished data, complete with index files,
news feeds and assets. It's ready to get uploaded or viewed directly.''',
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
    requires = ["BeautifulSoup", "Babel", "Mako"],
    scripts = ["scripts/website"],
    data_files = data_files
)
