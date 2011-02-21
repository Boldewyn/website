# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import aa
%>\
<%def name="list(articles, cls=None)">
  <ul\
    % if cls is not None:
      class="${cls}"\
    % endif
  >
    % for article in articles:
      <li>
        <a class="h" href="${article.live_path | aa}">${article.headers.title | n}</a>
        <div class="abstract">${article.headers.description | n}</div>
      </li>
    % endfor
  </ul>
</%def>
