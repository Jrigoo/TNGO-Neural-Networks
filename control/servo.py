# Import libraries
import RPi.GPIO as GPIO
import time

# Set GPIO numbering mode
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32,GPIO.OUT)
servo = GPIO.PWM(32,50) # pin 11 for servo, pulse 50Hz
servo.start(0)

# Loop to allow user to set servo angle. Try/finally allows exit
# with execution of servo.stop and GPIO cleanup :)
try:
    while True:
        #Ask user for angle and turn servo to it
        angle = float(input('Enter angle between 0 & 180: '))
        servo.ChangeDutyCycle(2+(angle/18))
        time.sleep(0.5)
        servo.ChangeDutyCycle(0)
except Exception as e:
    print("an error has ocurred")
    print(e)

finally:
    #Clean things up at the end
    servo.stop()
    GPIO.cleanup()
    print("Servo Stop")
