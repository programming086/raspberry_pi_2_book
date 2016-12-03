#!/bin/bash
if [ -d /tmp/stream ];then
        echo "/tmp/stream already created"
else
        mkdir /tmp/stream
fi

if [ -f /tmp/stream/pic.jpg ];then
        echo "raspistill already running"
else
        raspistill -w 320 -h 240 -q 5 -o /home/pi/webiopi/examples/servo-camera/pic.jpg -tl 100 -t 9999999&
fi
mjpg_streamer -i "input_file.so -f /home/pi/webiopi/examples/servo-camera" -o "output_http.so -w /home/pi/webiopi/examples/servo-camera"