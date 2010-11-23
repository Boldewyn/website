""""""


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
    for article in articles:
        a_tags = article.headers.get('SUBJECT', [])
        for a_tag in a_tags:
            if a_tag not in tags:
                tags[a_tag] = []
            tags[a_tag].append(article)
    for tag, a in tags.iteritems():
        description = None
        if os.path.exists("_doc/%s.tag.html" % tag):
            description = open("_doc/%s.tag.html" % tag).read()
        template_engine.render_paginated("tag", "tag/"+
                        tag+"/index.html", **locals())
        render_feed(a, "tag/%s" % tag)


def render_archives(articles):
    """"""
    dates = {}
    for article in articles:
        d = article.headers['DATE'].strftime("%Y/%m")
        if d not in dates:
            dates[d] = []
        dates[d].append(article)
    for date, a in dates.iteritems():
        template_engine.render_paginated("archive", "archive/"+
                        date+"/index.html", **locals())
        render_feed(a, "archive/%s" % date)


def render_indexes(articles):
    """"""
    cats = {}
    for article in articles:
        if article.category not in cats:
            cats[article.category] = []
        cats[article.category].append(article)
        if "/" in article.category:
            rootcat = article.category.split("/")[0]
            if rootcat not in cats:
                cats[rootcat] = []
            cats[rootcat].append(article)
    for category, a in cats.iteritems():
        if category == "":
            if not os.path.isfile(settings.BUILD_TARGET+"/index.html"):
                template_engine.render_paginated("index", "index.html",
                                                a=articles, articles=articles)
            render_feed(articles, category)
        elif not os.path.isfile(settings.BUILD_TARGET+"/"+category+"/index.html"):
            description = None
            if os.path.exists("_doc/%s.category.html" % category):
                description = open("_doc/%s.category.html" % category).read()
            template_engine.render_paginated("category", category+
                            "/index.html", **locals())
            render_feed(a, category)


def render_feed(all_articles, category=""):
    """Render the atom newsfeed"""
    articles = all_articles[:settings.get("FEED_LENGTH", len(all_articles))]
    author = dict(settings.DEFAULTS)['AUTHOR']
    updated = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    link = settings.URL+category+"/index.html"
    title = dict(settings.DEFAULTS)['TITLE']
    if category.startswith("tag/"):
        title = u"Tag \u201C%s\u201D \u2014 %s" % (category[4:], title)
    elif category.startswith("archive/"):
        title = u"Archive for %s \u2014 %s" % (category[8:], title)
    elif category != "" and category in settings.CATEGORY:
        title = u"Category \u201C%s\u201D \u2014 %s" % (settings.CATEGORY[category]['title'], title)
    id = settings.URL + category
    template_engine.render_template("feed", category+"/feed.xml", **locals())

