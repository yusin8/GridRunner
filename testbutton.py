import RPi.GPIO as GPIO
import time


button_pin = 21 
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        button_state = GPIO.input(button_pin)
        if button_state == False:
            print("pressed button.")
            while GPIO.input(button_pin) == False:
                time.sleep(0.1)  
        time.sleep(0.1)  
except KeyboardInterrupt:
    GPIO.cleanup()
