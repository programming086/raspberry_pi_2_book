#!/usr/bin/python

import serial, time, datetime, os, subprocess
import MySQLdb as db

#initialization and open the port
ser = serial.Serial()
ser.port = "/dev/ttyAMA0"
#ser.port = "/dev/ttyS2"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS 
ser.parity = serial.PARITY_NONE 
ser.stopbits = serial.STOPBITS_ONE 
#ser.timeout = None          #block read
ser.timeout = 1            #non-block read
#ser.timeout = 2              #timeout block read
ser.xonxoff = False     
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False       #disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2     #timeout for write

try: 
    ser.open()
except Exception, e:
    print "error open serial port: " + str(e)
    exit()

if ser.isOpen():
    try:
      ser.flushInput() #flush input buffer, discarding all its contents
      ser.flushOutput()#flush output buffer, aborting current output 
      con = db.connect(host="localhost", user="root", passwd="191066", db="my_project1")
      cur = con.cursor()
      while True:
        response = ser.readline()
        if response=='':
          pass
        else:
           print("read data: " + response)
           cur.execute('SET NAMES `utf8`')
           cur.execute('SELECT `ID` FROM `base_keys` WHERE `key`='+str(response)+' ')
           print cur.rowcount
           if cur.rowcount>0:
             id_key=0;
             for row in cur:
                id_key=row[0]
             dt = datetime.datetime.now() 
             photo=str(time.mktime(dt.timetuple()))+".jpg"
             time_event=datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
             print time_event
             print id_key
             print time.time()
             insertstmt=("insert into input_events (id_key,photo,time_event) values ('%d','%s','%s')" % (id_key,photo,time_event))
             cur.execute(insertstmt)
             #
             os.system('raspistill -o images/'+photo+' ')

      ser.close()
    except Exception, e1:
      print "error communicating...: " + str(e1)
else:
    print "cannot open serial port "
