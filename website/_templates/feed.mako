# -*- coding: utf-8 -*-
<%!
from website._webtools.templatedefs import aa, strip_tags
%>\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>${_(title)}</title>
  <link href="${link | aa}"/>
  <link rel="self" href="${settings.URL_PARTS[0]}://${settings.URL_PARTS[1]}${aa(url)}"/>
  <updated>${updated}</updated>

  <author>
    <name>${author}</name>
  </author>
  <id>${id}</id>

  % for article in a:
    <entry>
      <title>${article.headers.title | n,strip_tags}</title>
      <link href="${settings.URL_PARTS[0]}://${settings.URL_PARTS[1]}${aa(article.url)}"/>
      <id>${settings.URL_PARTS[0]}://${settings.URL_PARTS[1]}${aa(article.url)}</id>
      <updated>${article.headers.date.isoformat("T")}</updated>
      <summary>${article.headers.description}</summary>
    </entry>
  % endfor

</feed>
