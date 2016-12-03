import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)
spi.mode = 3
spi.max_speed_hz = 4000000

count = 0
while True:
    tx = [1, 2, 3, 4 ,5 ,6, count]
    print "Sending " + str(tx)
    resp = spi.xfer2(tx)
    print "Received" + str(resp)
    count += 1
    if count > 255: count = 0
    time.sleep(1)