# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import laa
%>\
<%inherit file="base.mako"/>\
\
<section id="content" class="archive">\
<h1>${_(u"Archive for %s") % xdate}</h1>\
<%namespace name="article_list" file="article_list.mako" />\
${article_list.list(a, "archive")}\
<%namespace name="page" file="paginate.mako" />\
${page.paginate(pag)}\
</section>\
\
<%def name="get_title()">\
${_(u"Archive for %s") % xdate} — \
</%def>\
\
<%def name="head()">\
<link rel="alternate" type="application/atom+xml" title="${_("Feed for %s") % xdate}" href="${laa(lang, "archive/%s/feed.xml" % xdate)}"/>\
</%def>\
