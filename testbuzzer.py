import RPi.GPIO as GPIO
import time


buzzer_pin = 17  

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer_pin, GPIO.OUT)


pwm = GPIO.PWM(buzzer_pin, 1000)  
pwm.start(50)  

try:
    for _ in range(5):
        pwm.ChangeFrequency(1000)  
        time.sleep(1)
        pwm.ChangeFrequency(500)  
        time.sleep(1)
    pwm.stop()

finally:
    GPIO.cleanup()
