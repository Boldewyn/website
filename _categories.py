""""""


import os
from _templates import template_engine


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


def render_indexes(articles):
    """"""
    categories = {}
    for article in articles:
        if article.category not in categories:
            categories[article.category] = []
        categories[article.category].append(article)
        if "/" in article.category:
            rootcat = article.category.split("/")[0]
            if rootcat not in categories:
                categories[rootcat] = []
            categories[rootcat].append(article)
    for category, a in categories.iteritems():
        if category+"/index.html" not in a:
            description = None
            if os.path.exists("_doc/%s.category.html" % category):
                description = open("_doc/%s.category.html" % category).read()
            template_engine.render_paginated("category", category+
                            "/index.html", **locals())

