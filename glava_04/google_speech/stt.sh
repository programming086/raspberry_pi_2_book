export AUDIODEV="hw:0"
echo "speaking ..."
arecord -B --buffer-time=1000000 -f dat -r 16000 -d 4 -D plughw:1,0 send.wav

echo "wav - flac"
flac -f -s send.wav -o send.flac  

echo "Converting Speech to Text..."
wget -q -U "Mozilla/5.0" --post-file send.flac --header "Content-Type: audio/x-flac; rate=16000" -O - "http://www.google.com/speech-api/v1/recognize?lang=en-us&client=chromium" | cut -d\" -f12  > stt.txt
 
echo "You Said:"
value=`cat stt.txt`
echo "$value"
