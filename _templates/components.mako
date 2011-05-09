# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import laa, static
%>\
\
<%def name="category_title(category)">\
<%
  try:
    title = _(settings.CATEGORY[category]["title"])
  except:
    title = category
%>\
${title}\
</%def>\
\
<%def name="show_sitesearch(img=None)">\
<form class="searchfield" method="get" action="${laa(lang, 'search')}">\
<p><input type="search" name="q"/> \
% if img:
<input type="image" src="${img}" alt="${_(u'search')}"/>\
% else:
<input type="submit" value="${_(u'search')}"/>\
% endif
</p></form>\
</%def>\
\
<%def name="show_tagcloud()">\
% if tagcloud:
<div class="tagcloud"><h2>${_(u"Tags")}</h2><p>\
% for tag, t, n in tagcloud:
<a class="tc_${str(t)}" rel="tag" href="${laa(lang, "tag/%s/" % tag)}" title="\
% if n == 1:
${_(u"one article")}\
% else:
${_(u"%s articles") % n}\
%endif
">${tag}</a> \
% endfor
</p></div>\
% endif
</%def>\
\
<%def name="show_archives()">\
% if archives:
<div class="archives"><h2>${_(u"Archive")}</h2><ul>\
% for d in archives:
<li><a href="${laa(lang, '/archive/%s/' % d)}">${d}</a></li>\
% endfor
</ul></div>\
% endif
</%def>\
\
<%def name="show_latest_articles()">\
% if latest_articles and len(latest_articles):
<div class="latest"><h2>${_(u"Latest Articles")}</h2><ul>\
% for art in latest_articles:
<li><a href="${laa(lang, art.url)}">${art.headers.title | n}</a></li>\
% endfor
</ul></div>\
% endif
</%def>\
\
<%def name="show_navigation(home=True,extra=[])">\
<ul>\
% if home:
<li class="home"><a href="${settings.URL}" rel="home">${_(u"Home")}</a></li>\
% endif
% if categories:
% for category in categories:
<li><a href="${laa(lang, category+"/")}">${self.category_title(category)}</a></li>\
% endfor
% endif
% for url, title in extra:
<li><a href="${url}">${title}</a></li>\
% endfor
</ul>\
</%def>\
