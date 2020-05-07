import Jetson.GPIO as GPIO
import time
# GPIO.setwarnings(False) # suppresses GPIO warnings
GPIO.setmode(GPIO.BOARD)
GREEN = 40
GPIO.setup(GREEN, GPIO.OUT)
RED = 38
GPIO.setup(RED, GPIO.OUT)

GPIO.setwarnings(False)
print("ON")
GPIO.output(GREEN,1)
time.sleep(5)
print("OFFFFF")

GPIO.output(GREEN,0)
time.sleep(5)

# GPIO.cleanup()