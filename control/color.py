import RPi.GPIO as GPIO
import time


S3 = 11
S2 = 13
COLOR_OUT = 15

""" 
Red -> Low, Low
Green -> High, High
Blue -> Low, High

"""

GPIO.setmode(GPIO.BOARD)
GPIO.setup(COLOR_OUT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(S2,GPIO.OUT)
GPIO.setup(S3,GPIO.OUT)

def pulseIn(pin, timeout=1):
    # Wait for the pulse to start (LOW to HIGH)
    start_time = time.time()
    while GPIO.input(pin) == GPIO.LOW:
        if time.time() - start_time > timeout:
            return 0

    # Measure the duration of the pulse (HIGH to LOW)
    start_time = time.time()
    while GPIO.input(pin) == GPIO.HIGH:
        if time.time() - start_time > timeout:
            return 0

    pulse_duration = (time.time() - start_time)*1e6 

    return pulse_duration

try:
    while True:
        # Red color detection
        GPIO.output(S2,GPIO.LOW)
        GPIO.output(S3,GPIO.LOW)
        red = round(pulseIn(COLOR_OUT),3)

        # Green
        GPIO.output(S2,GPIO.HIGH)
        GPIO.output(S3,GPIO.HIGH)
        green = round(pulseIn(COLOR_OUT),3)

        # Blue
        GPIO.output(S2,GPIO.LOW)
        GPIO.output(S3,GPIO.HIGH)
        blue = round(pulseIn(COLOR_OUT),3)

        average = round((red + green + blue)/3,2)
        print(f"RGB: [{red} {green} {blue}], Average: {average}")
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Closed.")
    GPIO.cleanup()