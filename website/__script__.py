

import os
import re
import sys
import logging
from datetime import datetime
from urlparse import urlparse
from . import __main__ as main


logger = logging.getLogger("website.script")


def help(*args):
    print "usage: website [COMMAND]"
    return 0


def init(*args):
    logger.info("Create new website")
    if len(args) == 0:
        target = "."
    else:
        target = args[0]
    if os.path.isdir(target):
        if os.listdir(target) != []:
            sys.stderr.write("The directory %s is not empty.\n" % target)
            exit(1)
    else:
        try:
            logger.info("Create directory %s" % target)
            os.mkdir(target)
        except OSError:
            sys.stderr.write("Cannot create directory %s.\n" % target)
            exit(2)
    os.chdir(target)
    os.mkdir("_articles")
    os.mkdir("_templates")
    conf = open("_config.py", "w")
    conf.write("""# Config file for this website
# uncomment the following line for l10n support:
# _ = lambda s: s

""")
    url = raw_input("Base URL (e.g., http://example.com/blog): ").rstrip("/") + "/"
    if not re.match(r"[a-z0-9_-]+:", url):
        url = "http://" + url
    conf.write("""URL = "%s"\n\n""" % url)
    title = raw_input("Title of the website: ")
    conf.write("""TITLE = "%s"\n\n""" % title)
    name = raw_input("Your name: ")
    conf.write("""DEFAULTS = {\n    "AUTHOR": "%s"\n}\n\n""" % name)
    email = raw_input("Your email address (optional): ")
    if email:
        conf.write("""EMAIL = "%s"\n\n""" % email)
    lang = raw_input("Website language (optional, two-letter language code): ")
    if lang:
        conf.write("""LANGUAGE = "%s"\n\n""" % lang)
    disqus = raw_input("Your Disqus username (optional): ")
    if disqus:
        conf.write("""DISQUS_NAME = "%s"\n\n""" % disqus)
    conf.close()
    logger.info("Create example article")
    art = open("_articles/first_post.html", "w")
    art.write("""Title: My First Post
Date: %s

<p>This is my first post. See, how simple this is?</p>""" % datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    art.close()
    if urlparse(url).path.lstrip("/") == "":
        open("robots.txt", "w").close()
        open("humans.txt", "w").close()
    return 0


def make(*args):
    if "_config.py" not in os.listdir("."):
        logger.error("This seems to be no website project.")
        exit(1)
    return main.main()


def makelang(*args):
    if "_config.py" not in os.listdir("."):
        logger.error("This seems to be no website project.")
        exit(1)
    try:
        from babel.messages import frontend
    except ImportError:
        logger.error("Cannot find pybabel.")
        exit(2)
    if not os.path.isdir("_locale"):
        os.mkdir("_locale")
    frontend.CommandLineInterface().run(["pybabel", "extract", "-F", os.path.dirname(__file__)+"/_locale/babel.cfg", "-o", "_locale/website.pot", ".", "_articles", "_templates"])
    return 0


commands = {
    "help": help,
    "init": init,
    "make": make,
    "makelang": makelang,
}
