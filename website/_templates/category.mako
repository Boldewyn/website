# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import laa
%>\
<%inherit file="base.mako"/>\
<%namespace name="comp" file="components.mako" />\
\
<section id="content" class="category">\
<h1>${comp.category_title(category)}</h1>\
% if description:
<section class="description">${description | n}</section>\
% endif
<%namespace name="article_list" file="article_list.mako" />\
${article_list.list(a)}\
<%namespace name="page" file="paginate.mako" />\
${page.paginate(pag)}\
</section>\
\
<%def name="get_title()">\
${_(u"Category “%s”") % category} — \
% if pag and pag["pages"] and pag["cur"] > 1:
${_("Page %s") % pag["cur"]} — \
% endif
</%def>\
\
<%def name="head()">\
<link rel="alternate" type="application/atom+xml" title="${_("Feed for category %s") % category}" href="${laa(lang, "%s/feed.xml" % category)}" />\
</%def>\
