# -*- coding: utf-8 -*-
<%!
from _webtools.templatedefs import jsq, strip_tags
%>\
<%page args="_, lang, article" />\

  % if "no-discussion" not in article.headers.status and "DISQUS_NAME" in settings:
    <section class="discussion">
      <div id="disqus_thread"></div>
      <script type="text/javascript">
        var disqus_shortname = '${settings.DISQUS_NAME}';
        var disqus_identifier = "${article.path | jsq}";
        var disqus_title = "${article.headers.title | n,strip_tags,jsq}";
        % if settings.DEBUG:
          var disqus_developer = 1;
        % endif
      </script>
      <script type="text/javascript" src="http://${settings.DISQUS_NAME}.disqus.com/embed.js" async="async"></script>
      <p class="dsq-brlink">
        <a href="http://${settings.DISQUS_NAME}.disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
      </p>
    </section>
  % endif

