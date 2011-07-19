# -*- coding: utf-8 -*-
<%!
from website._webtools.templatedefs import aa, laa
%>\
<%inherit file="base.mako"/>
<%namespace name="orig" file="article.mako" />

<%text><?php
$success = False;
$name = v('name');
$mail = filter_var(v('mail'), FILTER_VALIDATE_EMAIL);
$subj = v('subj');
$text = str_replace("\r\n", "\n", v('text'));
$honey = v('hp');
$lang = '</%text>${lang}<%text>';
$msg = '';

if (! v('sent')) {
} elseif ($mail && $name && $text && ! $honey) {
    if (! $subj) {
        if (preg_match('/^.{1,80}\n\n/', $text)) {
            list($subj, $text) = explode("\n\n", $text, 2);
        } else {
            $subj = "-no subject-";
        }
    }
    $headers = "From: \"$name\" <$mail>\r\n" .
               "X-Mailer: PHP/".phpversion()."\r\n".
               "X-Sender-IP: ${_SERVER['REMOTE_ADDR']}\r\n".
               "Content-type: text/plain; charset=UTF-8";
    $xtext = $text."\n\n".
        "--------------------------------------------\n".
        "</%text>${_(u"Sent from the contact form at")}<%text>\n".
        "</%text>${aa(url)}<%text>\n";
    $success = mail("</%text>${settings.EMAIL}<%text>", $subj, $xtext, $headers);

    if ($success) {
        $msg = '<section class="success"><p></%text>${_(u'The e-mail was successfully sent.')}<%text></p></section>';
    } else {
        $msg = '<section class="error"><p></%text>${_(u'An unknown error occurred. Please try later.')}<%text></p><ul>';
    }
} else {
    $msg = '<section class="error"><p></%text>${_(u'Please correct the following errors:')}<%text></p><ul>';
    if ($mail == False) { $msg .= '<li></%text>${_(u'The E-Mail address is missing or wrong.')}<%text></li>'; }
    if ($name == '') { $msg .= '<li></%text>${_(u'Please tell me your name.')}<%text></li>'; }
    if ($text == '') { $msg .= '<li></%text>${_(u'There is no text.')}<%text></li>'; }
    if ($honey != '') { $msg .= '<li></%text>${_(u'You have put text in a field, where you shouldn’t have.')}<%text></li>'; }
    $msg .= '</ul></section>';
}

function h($s) {
    return htmlspecialchars($s);
}

function v($s) {
    if (array_key_exists($s, $_POST)) {
        return trim(preg_replace('/[\x00-\x08\e\x7F\\\\]/u', '?', $_POST[$s]));
    } else {
        return '';
    }
}
?></%text>


<article id="content" class="hentry" \
  % if lang != article.headers.language:
    xml:lang="${article.headers.language}"\
  % endif
>
  % if prev_article:
    <p class="article_nav article_prev">
      <a href="${laa(lang, prev_article.url)}" title="${prev_article.headers.title}">&lt; ${_(u"previous")}</a>
    </p>
  % endif

  % if next_article:
    <p class="article_nav article_next">
      <a href="${laa(lang, next_article.url)}" title="${next_article.headers.title}">${_(u"next")} ></a>
    </p>
  % endif

  <%include file="article/head.mako" args="_=_, lang=lang, article=article" />

  <section class="entry-content">
    ${content | n}
  </section>

  <?php echo $msg; ?>

  <%text><?php if (! $success): ?></%text>
  <form method="POST" action="${aa(url)}" class="contact">
  <?php else: ?>
  <section class="contact form">
  <?php endif ?>
    <p>
      <label for="contact_name">${_(u"Name:")}</label>
      <input type="text" name="name" id="contact_name" value="<?php echo h($name)?>" />
    </p>
    <p>
      <label for="contact_mail">${_(u"E-Mail:")}</label>
      <input type="text" name="mail" id="contact_mail" value="<?php echo h(v('mail'))?>" />
    </p>
    <p>
      <label for="contact_subj">${_(u"Subject:")}</label>
      <input type="text" name="subj" id="contact_subj" value="<?php echo h($subj)?>" />
    </p>
    <p>
      <label for="contact_text">${_(u"Your Message:")}</label>
      <textarea name="text" id="contact_text"><?php echo h($text)?></textarea>
    </p>
    <p class="honezpot">
      <label for="contact_hp">${_(u"Please leave this field empty!")}</label>
      <input type="text" name="hp" id="contact_hp" value="<?php echo h($honey)?>" />
    </p>
    <%text><?php if (! $success): ?></%text>
    <p>
      <input type="hidden" name="sent" value="1" />
      <input type="submit" value="${_(u"Send e-mail")}" />
    </p>
    <?php endif ?>
  </form>
  <%text><?php if (! $success): ?></%text>
  </form>
  <?php else: ?>
  </section>
  <?php endif ?>

  <%include file="article/foot.mako" args="_=_, lang=lang, article=article" />

</article>

<%def name="get_title()">\
${orig.get_title()}
</%def>

<%def name="head()">
${orig.head()}
</%def>
