#!/usr/bin/python

from Adafruit_CharLCD import Adafruit_CharLCD
from subprocess import * 
from time import sleep, strftime
from datetime import datetime

lcd = Adafruit_CharLCD()

#cmd = "ip addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1"
cmd1 = "cat /proc/loadavg"
cmd2 = "/opt/vc/bin/vcgencmd measure_temp"

lcd.begin(16,2)

def run_cmd(cmd):
        p = Popen(cmd, shell=True, stdout=PIPE)
        output = p.communicate()[0]
        return output

lcd.clear()
lcd.message("  Adafruit 16x2\n  Standard LCD")
sleep(3)

while 1:
	lcd.clear()
	load = run_cmd(cmd1)
	temp = run_cmd(cmd2)
	#lcd.message(datetime.now().strftime('%b %d  %H:%M:%S\n'))
	#lcd.message('IP %s' % ( ipaddr ) )
	loads=load.split(' ')
	loadavg=int(float(loads[0])*100)
	lcd.message("loadavg="+str(loadavg)+"%\n" )
	lcd.message(temp )
	sleep(2)

GPIO.cleanup()
