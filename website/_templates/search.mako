# -*- coding: utf-8 -*-
<%inherit file="_templates/base.mako"/>

<section id="content">
<?php

$q = isset($_GET['q'])? $_GET['q'] : '';
$results = array();
$tmp = array();

if ($q) {
  $db = new PDO('sqlite:'.dirname(__FILE__).'/index.sqlite');
  $terms = preg_split('/\s+/', trim(strtolower($q)));
  $stm = $db->prepare('SELECT p FROM terms WHERE t LIKE ?');
  foreach ($terms as $t) {
    if (strlen($t) > 1) {
      if (strlen($t) > 2) {
        $stm->execute(array("%$t%"));
      } else {
        $stm->execute(array("$t%"));
      }
      $x = $stm->fetchAll(PDO::FETCH_COLUMN);
      if (count($x)) {
        $tmp[$t] = $x;
      }
    }
  }
  $db = null;
}

foreach ($tmp as $k => $v) {
  foreach ($v as $path) {
    if (array_key_exists($path, $results)) {
      $results[$path][0] += 1;
      if (! in_array($k, $results[$path][4])) {
        $results[$path][4][] = $k;
      }
    } else {
      list($title, $description) = get_title($path);
      $mtime = get_mtime($path);
      $results[$path] = array(1, $title, $description, $mtime, array($k));
    }
  }
}
ksort($results);
uasort($results, 'mysort');

?>
  <form method="GET" action="" class="searchform">
    <h1>${_(u"Search this Site")}</h1>
    <p>
      <input type="text" autofocus="autofocus" name="q" id="q" value="<?php echo h($q) ?>" />
      <input type="submit" value="${_(u"search")}" />
    </p>
  </form>
  <?php if (count($results)): ?>
  <section class="search-results">
    <h2>${_(u"Results")}</h2>
    <p>
      <?php printf("${_(u"I found %s results for the query “%s”:")}", count($results), "<var>".h($q)."</var>");?>
    </p>
    <ul class="hfeed">
      <?php foreach ($results as $p => $c):?>
        <li>
          <time class="updated" datetime="<?php echo $c[3]['year']?>-<?php echo $c[3]['mon']?>-<?php echo $c[3]['mday']?>">\
<span class="date-day"><?php echo $c[3]['mday']?></span>\
<span class="date-month"><?php echo $c[3]['mon']?> ’<?php echo substr($c[3]['year'], 2)?></span>\
</time>
          <a class="entry-title bookmark" href="<?php echo h($p)?>"><?php echo h($c[1])?></a>
          <div class="entry-summary"><?php if ($c[0] == 1) {
      echo "(<em>${_(u"1 match")}</em>)";
  } else {
      printf("(<em>${_(u"%d matches")}</em>)", $c[0]);
  }?> - <?php echo $c[2]?></div>
        </li>
      <?php endforeach ?>
    </ul>
  </section>
  <?php elseif ($q): ?>
    <section class="error">
      <p>${_(u"There are no results for this query.")}</p>
    </section>
  <?php else: ?>
    <p>${_(u"Please enter a search term.")}</p>
  <?php endif; ?>
</section>


<?php

function h($s) {
    return htmlspecialchars(preg_replace('/[\p{C}]/u', '', $s));
}

function get_title($p) {
  $contents = file_get_contents(ltrim($p, "/"));
  if ($contents) {
    $title = preg_replace('/^.*<h1[^>]*>(.*?)<\/h1>.*$/s', '\\1', $contents);
    $description = "";
    if (strpos($contents, 'name="description"') !== False) {
      $description = preg_replace('/^.*<meta\s+(name="description"\s+content="(.*?)"|content="(.*?)"\s+name="description").*$/s', '\\2\\3', $contents);
      if ($description == $contents) {
        $description = "";
      }
    }
    return array($title, $description);
  } else {
    return array($p, "");
  }
}

function get_mtime($p) {
  $time = filemtime(ltrim($p, "/"));
  return getdate($time);
}

function mysort($a, $b) {
  if (count($a[4]) < count($b[4])) {
    return 1;
  } elseif (count($a[4]) > count($b[4])) {
    return -1;
  } elseif ($a[0] == $b[0]) {
    return 0;
  } else {
    return ($a[0] < $b[0]) ? 1 : -1;
  }
}

?>

<%def name="head()">\
  <meta name="robots" content="noindex,follow" />
</%def>
