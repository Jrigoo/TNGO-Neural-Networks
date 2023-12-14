import RPi.GPIO as GPIO
import time

# Define the motor driver pins
A = 8
C = 10
B = 12
D = 16

# Set the GPIO mode and setup the motor driver pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(A, GPIO.OUT)
GPIO.setup(C, GPIO.OUT)
GPIO.setup(B, GPIO.OUT)
GPIO.setup(D, GPIO.OUT)

# Define the step sequence
step_sequence = [
    [1, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 1],
    [1, 0, 0, 1]
]

# Function to move the stepper motor
def move_stepper(steps, dir=1):
    step_delay = 0.001
    steps_left = steps
    last_step_time = 0
    step_number = 0

    while steps_left > 0:
        now = time.time()
        if (now - last_step_time) >= step_delay:
            last_step_time = now

            if dir == 1:
                step_number += 1
                if step_number == 4:
                    step_number = 0
            else:
                if step_number == 0:
                    step_number = 4
                step_number -= 1

            steps_left -= 1
            current = step_number % 4
            GPIO.output(A, step_sequence[current][0])
            GPIO.output(C, step_sequence[current][1])
            GPIO.output(B, step_sequence[current][2])
            GPIO.output(D, step_sequence[current][3])

if __name__ == "__main__":
    steps = int(input("Number of steps: "))
    dir = int(input("Direction: "))
    move_stepper(steps,dir)

    GPIO.cleanup()
