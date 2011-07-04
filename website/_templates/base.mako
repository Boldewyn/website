# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import static, aa, laa
%>\
<%namespace name="comp" file="components.mako" />\
<!DOCTYPE html SYSTEM "about:legacy-compat">\
<html xmlns="http://www.w3.org/1999/xhtml" prefix="dc: http://purl.org/dc/terms/" xml:lang="${lang or 'en'}" lang="${lang or 'en'}">\
<head>\
<meta charset="UTF-8"/>\
<!--[if lt IE 9]><script src="${'html5.js' | static}"></script><![endif]-->\
<link rel="stylesheet" href="${'style.css' | static}"/>\
<link rel="profile" href="http://www.w3.org/2003/g/data-view"/>\
<link rel="alternate" type="application/atom+xml" href="${laa(lang, "feed.xml")}"/>\
<link rel="shortcut icon" href="/favicon.ico"/>\
% if article:
<link rel="canonical" href="${settings.URL_PARTS[0]}://${settings.URL_PARTS[1]}${aa(article.url)}"/>\
% else:
<link rel="canonical" href="${settings.URL_PARTS[0]}://${settings.URL_PARTS[1]}${aa(url)}"/>\
% endif
<script src="${'script.js' | static}"></script>\
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>\
${self.head()}\
<title>\
% if hasattr(self, 'get_title'):
${self.get_title()}\
% endif
${_(settings.TITLE)}</title>\
</head>\
<body>\
<div id="global">\
${self.header()}\
<div id="body">\
${self.body()}\
${self.aside()}\
</div>\
${self.footer()}\
</div>\
${self.foot()}\
</body>\
</html>\
\
<%def name="head()"/>\
<%def name="foot()"/>\
\
<%def name="header()">\
<header id="header">\
<nav>\
${comp.show_navigation()}\
</nav>\
</header>\
</%def>\
\
<%def name="footer()">\
<footer>\
<p><a href="#header">${_(u"Back to the top")}</a></p>\
</footer>\
</%def>\
\
<%def name="aside()">\
<aside>\
${comp.show_sitesearch()}\
${comp.show_tagcloud()}\
${comp.show_archives()}\
${comp.show_latest_articles()}\
</aside>\
</%def>\
