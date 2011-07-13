""""""


import glob
import os
from datetime import datetime
from .templates import template_engine
from .settings import settings


def render(articles):
    render_tags(articles)
    render_archives(articles)
    render_indexes(articles)


def render_tags(articles):
    """"""
    tags = {}
    article = None
    for article in articles:
        a_tags = article.headers.get('SUBJECT', [])
        for a_tag in a_tags:
            if a_tag not in tags:
                tags[a_tag] = []
            tags[a_tag].append(article)
    del article
    for tag, a in tags.iteritems():
        description = None
        if os.path.exists("_doc/%s.tag.html" % tag):
            description = open("_doc/%s.tag.html" % category).read().decode("UTF-8")
        template_engine.render_paginated("tag", "tag/"+
                        tag+"/index.html", **locals())
        render_feed(a, "tag/%s" % tag)


def render_archives(articles):
    """"""
    dates = {}
    article = None
    for article in articles:
        d = article.headers['DATE'].strftime("%Y/%m")
        if d not in dates:
            dates[d] = []
        dates[d].append(article)
        y = article.headers['DATE'].strftime("%Y")
        if y not in dates:
            dates[y] = []
        dates[y].append(article)
    del article
    for xdate, a in dates.iteritems():
        if len(xdate) == 4:
            date = datetime(int(xdate), 12, 31)
        else:
            date = datetime(int(xdate[:4]), int(xdate[5:7]), 1)
        template_engine.render_paginated("archive", "archive/"+
                        xdate+"/index.html", **locals())
        render_feed(a, "archive/%s" % xdate)


def render_indexes(articles):
    """"""
    cats = {}
    article = None
    for article in articles:
        if article.category not in cats:
            cats[article.category] = []
        cats[article.category].append(article)
        if "/" in article.category:
            rootcat = article.category.split("/")[0]
            if rootcat not in cats:
                cats[rootcat] = []
            cats[rootcat].append(article)
    del article
    for category, a in cats.iteritems():
        if category == "":
            if not has_index(settings.BUILD_TARGET):
                template_engine.render_paginated("index", "index.html",
                                                a=articles, articles=articles)
            render_feed(articles, category)
        elif not has_index(settings.BUILD_TARGET+"/"+category):
            description = None
            if os.path.exists("_doc/%s.category.html" % category):
                description = open("_doc/%s.category.html" % category).read().decode("UTF-8")
            template_engine.render_paginated("category", category+
                            "/index.html", **locals())
            render_feed(a, category)


def render_feed(all_articles, category=""):
    """Render the atom newsfeed"""
    _ = lambda s: s
    articles = all_articles[:settings.get("FEED_LENGTH", len(all_articles))]
    author = settings.DEFAULTS['AUTHOR']
    updated = datetime.utcnow().isoformat()[0:19]+"Z"
    link = (settings.URL+category).rstrip("/") + "/"
    title = settings.get("TITLE", "")
    if category.startswith("tag/"):
        title = _(u"Tag \u201C%(tag)s\u201D \u2014 %(title)s") % { 'tag': category[4:],
                                                                  'title': title }
    elif category.startswith("archive/"):
        title = _(u"Archive for %(date)s \u2014 %(title)s") % { 'date': category[8:],
                                                               'title': title }
    elif category != "" and category in settings.CATEGORY:
        title = _(u"Category \u201C%(category)s\u201D \u2014 %(title)s") % {
                    'category': settings.CATEGORY[category]['title'], 'title': title }
    id = settings.URL + category
    nolang = True
    template_engine.render_template("_templates/feed.mako",
                                    category+"/feed.xml", **locals())


def has_index(folder):
    """Look, if there is an index file in folder"""
    if not os.path.isdir(folder):
        return None
    candidates = glob.glob(folder+"/index.*")
    if len(candidates) == 0:
        return False
    for c in candidates:
        base = os.path.basename(c)
        probes = base.split(".")
        while len(probes) > 1 and probes[-1] in settings.known_extensions:
            probes.pop()
        if len(probes) == 1:
            return True
        else:
            continue
    return False



