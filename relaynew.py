import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40,GPIO.OUT)
GPIO.output(40,GPIO.HIGH)

try:
	GPIO.output(40,GPIO.LOW)
	print("This channel works!")
	time.sleep(1)
	GPIO.cleanup()
	

except KeyboardInterrupt:
	print("QUIT")
	GPIO.cleanup()
