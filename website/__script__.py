

import logging
import os
import sys
import traceback
from website._webtools.lib import argparse
from website._webtools.build import build
from website._webtools.bootstrap import bootstrap


logger = logging.getLogger("website")


def dispatch(*args):
    """Dispatch the right command (args[0])"""
    if len(args) == 0:
        return help()
    else:
        if args[0] in dict(commands):
            com = dict(commands)[args[0]]
            return com(*args[1:])
        else:
            return help(args[0])


def help(com=None):
    help.__doc__ = """usage: website COMMAND [OPTIONS]
where COMMAND is one of
  %s

Initializes and controls a website project. Use
  website help COMMAND
for detailed information.""" % ", ".join([n for n,c in commands])
    if com is None:
        print help.__doc__
    else:
        if com in [n for n,c in commands]:
            print dict(commands)[com].__doc__
        else:
            sys.stderr.write("Command %s not recognized.\n" % com)
            sys.stderr.flush()
            print help.__doc__
    return 0


def init(*args):
    """usage: website init NAME
Create a new website project.

Options:
    NAME        name of the project folder"""
    config = dict([
            ["URL", raw_input("Base URL (e.g., http://example.com/blog): ")],
            ["TITLE", raw_input("Title of the website: ")],
            ["DEFAULTS", {
                "AUTHOR": raw_input("Your name: ")
            }],
            ["EMAIL", raw_input("Your email address (optional): ")],
            ["LANGUAGE", raw_input("Website language (optional, two-letter language code): ")],
            ["DISQUS_NAME", raw_input("Your Disqus username (optional): ")],
    ])
    if len(args) == 0:
        target = "."
    else:
        target = args[0]
    if os.path.isdir(target):
        if os.listdir(target) != []:
            logger.critical("The directory %s is not empty" % target)
            raise ValueError
    return bootstrap(target, config)


def make(*args):
    """usage: website make
Compile the output."""
    if "_config.py" not in os.listdir("."):
        logger.error("This seems to be no website project.")
        exit(1)
    return build()


def makelang(*args):
    """usage: website makelang
Compile the language strings used in the project and store them in
_locale/website.pot."""
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


commands = (
    ("help", help),
    ("init", init),
    ("make", make),
    ("makelang", makelang),
 )


if __name__ == "__main__":
    try:
        r = dispatch(*sys.argv[1:])
        if not isinstance(r, int):
            r = 0
    except Exception:
        logger.critical(traceback.format_exc())
        r = 1
    sys.exit(r)


