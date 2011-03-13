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
        if (document.cookie.search(/nodisq=1/) === -1) {
          (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = 'http://' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
          })();
        } else {
          var a = document.createElement('a');
          a.setAttribute('href', '#');
          a.onclick = function () {
            document.cookie = 'nodisq=0; path=/';
            location.reload();
          };
          a.appendChild(document.createTextNode("${_(u'Discussion disabled due to privacy settings. Click here to re-enable.')}"));
          document.getElementById("disqus_thread").appendChild(a);
        }
      </script>
      <p class="dsq-brlink">
        <a href="http://${settings.DISQUS_NAME}.disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a>
      </p>
    </section>
  % endif

