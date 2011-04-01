# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import aa, strip_tags
%>\
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>${title}</title>
  <link href="${link | aa}"/>
  <updated>${updated}</updated>

  <author>
    <name>${author}</name>
  </author>
  <id>${id}</id>

  % for article in articles:
    <entry>
      <title>${article.headers.title | n,strip_tags}</title>
      <link href="${aa(article.url)}"/>
      <id>${article.headers.ID}</id>
      <updated>${article.headers.date.strftime("%Y-%m-%dT%H:%M:%S%z")}</updated>
      <summary>${article.headers.description}</summary>
    </entry>
  % endfor

</feed>
