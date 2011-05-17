<?php
/**
 * Debian: apt-get install php5-xmlrpc php5-curl
 */
/**
 * @brief xmlrpc format generator
 *        XMLRPC format:
 *        <?xml version="1.0" encoding="utf-8"?>
 *        <methodCall>
 *        <methodName>$method_name</methodName>
 *        <params>
 *        <param>
 *         <value>
 *           <$value_type>$value</$value_type>
 *         </value>
 *        </param>
 *        </params>
 *        </methodCall>
 *
 *        USAGE:
 *          $re = encode_xmlrpc('echo', array( array('string' => 'Linux test')) );
 *          $xml = xmlrpc_request('http://localhost/', $re);
 *          $xml = xmlrpc_decode($xml);
 *
 *          $re = encode_xmlrpc('echo', array( 0 => array('string' => 'Linux test'), 1 => array('string' => 'test') ));
 *          $xml = xmlrpc_request('http://localhost/', $re);
 *          $xml = xmlrpc_decode($xml);
 *
 * @param method string:xmlrpc function name
 * @param params array: array( 0 => array('type', $value), 1 => array('type', $value) )
 * @retval xmlrpc_format/false
 */
function encode_xmlrpc($method, $params)
{
    $method = htmlspecialchars($method);

    $response_pre = '<?xml version="1.0" encoding="utf-8"?>';
    $response_pre.= "<methodCall><methodName>$method</methodName>";
    $response_pre.= "<params>";

    // xmlrpc spec: http://www.xmlrpc.com/spec, allow tag list
    $allow_type = array('i4', 'int', 'boolean', 'string', 'double', 'dateTime.iso8604', 'base64');

    $response_mid = '';
    if (is_array($params)) {
        foreach ($params as $param) {
            foreach($param as $type => $val) {
                if(!in_array($type, $allow_type)) {
                    return false;
                }

                $val = htmlspecialchars($val);
                $response_mid .= "<param><value><$type>$val</$type></value></param>";
            }
        }
    }

    $response_post = '</params></methodCall>';

    return $response_pre . $response_mid . $response_post;
}

/**
 * @brief xmlrpc request
 * @param url xmlrpc url
 * @param method string:xmlrpc function name
 * @param params array: array( 0 => array('type', $value), 1 => array('type', $value) )
 * @retval array/false
 */
function request_xmlrpc($url, $method='', $params='') {
    if (empty($url) || empty($method) || empty($params)) {
        return false;
    }

    $postvar = encode_xmlrpc($method, $params);
    $res = postUrl($url, $postvar);
    $res = xmlrpc_decode($res);

    return $res;
}

/**
 * HTTP Post
 * @param url
 * @param postvar: args
 */
function postUrl($url, $postvar)
{
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER,1);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postvar);

    $res = curl_exec ($ch);
    curl_close ($ch);

    return $res;
}
?>
