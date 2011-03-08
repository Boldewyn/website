# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import aa, month
%>\
<%def name="list(articles, cls=None)">
  <ul class="article-list \
    % if cls is not None:
     ${cls}\
    % endif
    "
  >
    % for article in articles:
      <li>
        <span class="date"><span class="date-day">${str(article.headers.date.day)}</span><span class="date-month">${month(_, article.headers.date.month)} ’${str(article.headers.date.year)[2:]}</span></span>
        <a class="h" href="${article.live_path | aa}">${article.headers.title | n}</a>
        <div class="abstract">${article.headers.description | n}</div>
      </li>
    % endfor
  </ul>
</%def>
