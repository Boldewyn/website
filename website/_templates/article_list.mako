# -*- coding: utf-8 -*-
<%!
from website._webtools.templatedefs import laa, month
%>\
<%def name="list(articles, cls=None)">\
<ul class="hfeed \
% if cls is not None:
${cls}\
% endif
">\
% for article in articles:
<li class="hentry">\
<time class="updated" datetime="${article.headers.date.isoformat("T")}">\
<span class="date-day">${str(article.headers.date.day)}</span>\
<span class="date-month">${month(_, article.headers.date.month)} ’${str(article.headers.date.year)[2:]}</span>\
</time>\
<address class="author vcard"><span class="fn">${article.headers.author}</span></address>\
<a class="entry-title bookmark" href="${laa(lang, article.url)}">${article.headers.title | n}</a>\
<div class="entry-summary">${article.headers.description | n}</div>\
</li>\
% endfor
</ul>\
</%def>\
