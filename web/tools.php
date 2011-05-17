<?php
/**
 * function KeywordBold($string, $position_array)
 * example:
 $string = 'xxxxxxxxxxxxxxxxxxxxxxxxx';
 $position_array = array(
   0 => array (
     0 => 0,
     1 => 4
   ),
   1 => array (
     0 => 21,
     1 => 25
   )
 );
 */
function KeywordBold($string, $position_array)
{
    if (empty($string)) {
        return '';
    }

    $add_position = 0;
    for ($i=0, $c=count($position_array); $i<$c; $i++) {
        if (!isset($position_array[$i][0]) || !isset($position_array[$i][1])) {
            continue;
        }

        if (!is_numeric($position_array[$i][0]) || !is_numeric($position_array[$i][1])) {
            continue;
        }

        $len = mb_strlen($string, 'UTF-8');
        $pre = '';
        $mid = '';
        $aft = '';
        $get_unit = $position_array[$i][1] - $position_array[$i][0];

        $add_position = 7 * $i; // <b></b>

        // 0 ~ pre-keyword => string ~ pre-keyword
        $pre = mb_substr($string, 0, $position_array[$i][0] + $add_position, 'UTF-8');

        // mid => <b>keyword</b>
        $mid = mb_substr($string, $position_array[$i][0] + $add_position, $get_unit, 'UTF-8');

        // pre-keyword ~ end => pre-keyword ~ string
        $aft = mb_substr($string, $position_array[$i][1] + $add_position, $len, 'UTF-8');

        $string = $pre . '<b>' . $mid. '</b>' . $aft;
    }

    return $string;
}

function insWBR($str, $number = 30)
{
    $pattern = "/(.{$number})/";
    $replacement = "\1<wbr>";
    return preg_replace($pattern, $replacement, $str);
}

function getUserIp()
{
    //global $HTTP_ENV_VARS, $HTTP_SERVER_VARS, $HTTP_X_FORWARDED_FOR;
    $HTTP_ENV_VARS = $_ENV;
    $HTTP_SERVER_VARS = $_SERVER;

    if (getenv('HTTP_X_FORWARDED_FOR') != '') {
        $proxy_ip = (!empty($HTTP_SERVER_VARS['REMOTE_ADDR'])) ?
            $HTTP_SERVER_VARS['REMOTE_ADDR'] :
            ((!empty($HTTP_ENV_VARS['REMOTE_ADDR'])) ?
             $HTTP_ENV_VARS['REMOTE_ADDR'] : $REMOTE_ADDR);
        $client_ip = getenv('HTTP_X_FORWARDED_FOR');
    } else {
        $client_ip = (!empty($HTTP_SERVER_VARS['REMOTE_ADDR']))?
            $HTTP_SERVER_VARS['REMOTE_ADDR'] :
            ((!empty($HTTP_ENV_VARS['REMOTE_ADDR'])) ?
             $HTTP_ENV_VARS['REMOTE_ADDR'] : $REMOTE_ADDR);
        $proxy_ip = '';
    }

    return $client_ip;
}

function getPageHTML($total_data_num, $url, $b = 1, $n = 10)
{
    $page_nav = '';

    $totalpage = ceil($total_data_num/ $n);
    $curpage = ($b <= 0) ? 1 : ceil($b / $n);
    if ($b <= 0) {
        $b = 1;
    }

    if ($curpage - 1 > 0) {
        $page_nav .= "<span class=\"p\"><a href=\"$url&b=".($b-$n)."&n=$n\" title=\"上一頁\" class=\"pagelink\">上一頁</a></span>";
        if($curpage/$n <= 0.6)
            $firstpage = 1;
        else
            $firstpage = $curpage - floor($n/2);
    }else{
        $firstpage = 1;
    }

    if ($firstpage == 0) {
        $firstpage = 1;
    }

    //last page link
    $lastpage = ($firstpage + $n) > $totalpage ? $totalpage : $firstpage + $n - 1;

    for($i = $firstpage; $i <= $lastpage; $i++) {
        $page_nav .= '<span>';
        if ($curpage == $i) {
            $page_nav .= "<strong>$i</strong>";
        } else {
            $page_nav .= "<a href=\"$url&b=" . ((($i - 1) * $n)+1)  . "&n=$n\">$i</a>";
        }
        $page_nav .= '</span>';
    }
    if ($curpage + 1 <= $totalpage) {
        $page_nav .= "<span class=\"n\"><a href=\"$url&b=".($b+$n)."&n=$n\" title=\"下一頁\" class=\"pagelink\">下一頁</a></span>";
    }
    return $page_nav;
}
?>
