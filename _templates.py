""""""


import os
from mako.template import Template
from mako import exceptions
from mako.lookup import TemplateLookup
from _settings import settings


_dir = os.path.dirname(__file__)
_lookup = TemplateLookup(directories=["."], default_filters=["x"])


def render_template(template, path, **ctx):
    """"""
    ctx['settings'] = settings
    if "articles" in ctx and "categories" not in ctx:
        ctx["categories"] = get_categories(ctx["articles"])
    if "articles" in ctx and "tagcloud" not in ctx:
        ctx["tagcloud"] = get_tagcloud(ctx["articles"])
    if "articles" in ctx and "archives" not in ctx:
        ctx["archives"] = get_archives(ctx["articles"])
    path = os.path.abspath(path)
    tpl = Template(filename="_templates/"+template+'.mako',
                   lookup=_lookup, default_filters=["x"])
    if not os.path.isdir(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    to = open(path, 'w')
    try:
        to.write(tpl.render_unicode(**ctx).encode("UTF-8"))
    except:
        print exceptions.text_error_template().render()
        exit()
    to.close()


def get_tagcloud(articles, offset=1):
    """Get all tags from the categories"""
    tags = {}
    for article in articles:
        for tag in article.headers['SUBJECT']:
            if tag in tags:
                tags[tag] += 1
            else:
                tags[tag] = 1
    if offset > 1:
        for tag, n in tags.iteritems():
            if n < offset:
                del tags[tag]
    return tags


def get_categories(articles):
    """Get all categories from the articles"""
    categories = []
    for article in articles:
        if article.category not in categories:
            categories.append(article.category)
        if "/" in article.category:
            rootcat = article.category.split("/")[0]
            if rootcat not in categories:
                categories.append(rootcat)
    categories.sort()
    return categories


def get_archives(articles):
    """Get all archive links"""
    dates = []
    for article in articles:
        d = article.headers['DATE'].strftime("%Y/%m")
        if d not in dates:
            dates.append(d)
    return dates

