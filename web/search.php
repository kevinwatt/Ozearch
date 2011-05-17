<?php
include('rpc.php');
include('tools.php');
include('set.inc');

$n = (isset($_GET['n']) && is_numeric($_GET['n'])) ? $_GET['n'] : 10;
$b = (isset($_GET['b']) && is_numeric($_GET['b'])) ? $_GET['b'] : 1;
$p = (isset($_GET['p']) && !empty($_GET['p'])) ? trim($_GET['p']) : '';
$r = ''; // search result
$total_data_num = 0;
$total_page_num = 0;


$page = intval($b / $n);

$params = array( 0 => array('string' => $p), 1 => array('int' => $n), 2 => array('int' => $page) );

// query
if (!empty($p)) {
    $r = request_xmlrpc($url, $method, $params);
    $total_data_num = $r[0];
    $total_page_num = ceil($total_data_num / $n);

    $ip = getUserIp();
    $time = time();
    error_log("[$ip],[$time],[$p]\n", 3, LOG_FILE);
}

// for debug message
if ($debug && (isset($r['faultCode']) || isset($r['faultString']))) {
    echo "DEBUG:<br />";
    echo "faultCode: {$r['faultCode']} <br />";
    echo "faultString: {$r['faultString']} <br />";
    echo '<pre>';
    print_r($r);
    echo '</pre>';
}

// Search not found or some error.
if (isset($r['faultCode']) || isset($r['faultString'])) {
    $r = false;
}

?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
  <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
  <title>Open Search</title>
  <link rel="stylesheet" href="style.css" type="text/css" />
</head>
<body id="search">

<center>
<div id="logo"><a href="index.html"><img border="0" src="ozearch.jpeg" /></a></div>
<form name="search_form" action="search.php" method="get">
<input type="text" size="80" name="p" value="<?php echo htmlspecialchars($p); ?>" />
<input type="submit" value="查詢" />
</form>
</center>

<div class="pagenav">
<center>
<?php
$enc_p = urlencode($p);
$script_url = "search.php?p=$enc_p";
echo getPageHTML($total_data_num, $script_url, $b, $n);
?>
</center>
</div>

<?php
if (empty($p)) {
    echo '<center>';
    echo '沒有輸入任何關鍵字, 請輸入關鍵字查詢.';
    echo '</center>';
} else if (!$r || $r[0] == 0) {
    echo '<center>';
    echo '找不到和您的查詢- <span class="red">'.htmlspecialchars($p).'</span> -相符的資料<br />';
    echo '請改試其它字詞';
    echo '</center>';
} else {
?>

  <div id="total_data_num">
  <?php
  $end_num = $b+$n-1;
  if ($end_num > $total_data_num)
      $end_num = $total_data_num;
  ?>
    約有 <?php echo number_format($total_data_num); ?>項符合<span><?php echo htmlspecialchars($p); ?></span>的查詢結果，
    以下是第 <?php echo $b; ?>-<?php echo $end_num; ?>項。
  </div>

  <p style="height:10px;" />

  <ol>
  <?php for ($i=0, $c=count($r[1]); $i<$c; $i++) { ?>
    <li>
        <dl>
          <dt><a href="<?php echo urldecode($r[1][$i][3]); ?>"><?php echo (empty($r[1][$i][4]))?'No Title':KeywordBold($r[1][$i][4], $r[1][$i][6]); ?></a></dt>
          <dd>
          <ul>
            <li><?php echo KeywordBold($r[1][$i][0], $r[1][$i][5]); ?> ... </li>
            <li class="linkurl"><?php echo insWBR(urldecode($r[1][$i][3])); ?></li>
          </ul>
          </dd>
        </dl>
    </li>
  <?php } ?>
  </ol>

<?php
}
?>

<div class="pagenav">
<center>
<?php
$enc_p = urlencode($p);
$script_url = "search.php?p=$enc_p";
echo getPageHTML($total_data_num, $script_url, $b, $n);
?>
</center>
</div>

<!--
<script>
document.search_form.p.focus();
</script>
-->

</body>
</html>
