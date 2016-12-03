# Imports
import webiopi
import sys
import time
from subprocess import call

# Enable debug output
webiopi.setDebug()

# Retrieve GPIO lib
GPIO = webiopi.GPIO

SERVO1  = 23
SERVO2  = 23
LED1   = 25


def camera_start():
    return_code = call("/usr/share/webiopi/htdocs/app/Raspirobot/stream.sh", shell=True)

# Called by WebIOPi at script loading
def setup():
    webiopi.debug("Blink script - Setup")
    # Setup GPIOs
    GPIO.setFunction(SERVO1, GPIO.PWM)
    GPIO.setFunction(SERVO1, GPIO.PWM)
    GPIO.setFunction(LED1, GPIO.OUT)
    
    GPIO.pwmWriteAngle(SERVO1, 0)    # set to 0 (neutral)
    GPIO.pwmWriteAngle(SERVO2, 0)    # set to 0 (neutral)
    GPIO.digitalWrite(LED1, GPIO.HIGH)
    camera_start()

# Looped by WebIOPi
def loop():
    # Toggle LED each 5 seconds
    value = not GPIO.digitalRead(LED1)
    GPIO.digitalWrite(LED1, value)
    webiopi.sleep(5)        

# Called by WebIOPi at server shutdown
def destroy():
    webiopi.debug("Blink script - Destroy")
    # Reset GPIO functions
    GPIO.setFunction(SWITCH, GPIO.IN)
    GPIO.setFunction(SERVO, GPIO.IN)
    GPIO.setFunction(LED0, GPIO.IN)
    GPIO.setFunction(LED1, GPIO.IN)
