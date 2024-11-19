import RPi.GPIO as GPIO
import time


green_led_pin = 16  

GPIO.setmode(GPIO.BCM)
GPIO.setup(green_led_pin, GPIO.OUT)

try:
    for _ in range(10):
        GPIO.output(green_led_pin, GPIO.HIGH)  
        time.sleep(1)
        GPIO.output(green_led_pin, GPIO.LOW)  
        time.sleep(1)

finally:
    GPIO.cleanup()
