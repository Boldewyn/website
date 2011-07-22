""""""


import logging
import os
import pprint
import re
from datetime import datetime
from urlparse import urlparse


logger = logging.getLogger("website.bootstrap")


def bootstrap(target, config):
    """Create a new website project"""
    logger.info("Create new website")
    config = config or {}
    if os.path.isdir(target):
        if os.listdir(target) != []:
            logger.critical("The directory %s is not empty" % target)
            raise ValueError
    else:
        try:
            os.mkdir(target)
        except OSError:
            logger.critical("Cannot create directory %s" % target)
            raise
        else:
            logger.info("Create directory %s" % target)
    os.mkdir(os.path.join(target, "_articles"))
    os.mkdir(os.path.join(target, "_templates"))
    conf = open(os.path.join(target, "_config.py"), "w")
    conf.write("""# Config file for this website
# uncomment the following line for l10n support:
# _ = lambda s: s

""")
    if "URL" in config:
        config["URL"] = config["URL"].rstrip("/") + "/"
        if not re.match(r"[a-z0-9_-]+:", config["URL"]):
            config["URL"] = "http://" + config["URL"]
    else:
        config["URL"] = "http://localhost/"
    for k, v in config.iteritems():
        conf.write("%s = %s\n\n" % (k, pprint.pformat(v)))
    conf.close()
    logger.info("Create example article")
    art = open(os.path.join(target, "_articles/first_post.html"), "w")
    art.write("""Title: My First Post
Date: %s

<p>This is my first post. See, how simple this is?</p>""" % datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
    art.close()
    if urlparse(config["URL"]).path.lstrip("/") == "":
        open(os.path.join(target, "robots.txt"), "w").close()
        open(os.path.join(target, "humans.txt"), "w").close()


