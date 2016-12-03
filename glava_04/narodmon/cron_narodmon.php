<?php
 
define('SERIAL_DEVICE', '/dev/ttyACM0'); 
$fp = fopen(SERIAL_DEVICE, "w+");
if( !$fp) { 
 die("can\'t open " . SERIAL_DEVICE);
}
else
  print "open port - ok\n";
  sleep(5);
 
 if( fwrite($fp, "1" ))  {
  print "OK\n\n";
 }
 else {
  print "FAILED!!!\n\n";
 }
$cc="";
$x=true;
while($x==true){
   $c=fread($fp,1);
   if($c=="\n")
      $x=false;
   $cc=$cc.$c;
   }
 
$sdata="#B8:27:EB:83:A3:2C\n".str_replace("&","\n",$cc)."##";
print $sdata;
fclose($fp);

$fs = @fsockopen("tcp://narodmon.ru", 8283, $errno, $errstr);
if(!$fs) exit("ERROR(".$errno."): ".$errstr);
fwrite($fs, $sdata);
fclose($fs);
?>
