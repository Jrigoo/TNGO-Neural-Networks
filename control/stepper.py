import RPi.GPIO as gpio
import time

class Stepper:
    def __init__(self, dir_pin, step_pin, limit_pin):
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.limit_pin = limit_pin
        self.cw = 1
        self.ccw = 0
        self.delay = 0.01
    
        gpio.setmode(gpio.BOARD)
        gpio.setup(self.dir_pin, gpio.OUT)
        gpio.setup(self.step_pin, gpio.OUT)
        gpio.setup(self.limit_pin, gpio.IN, pull_up_down = gpio.PUD_UP)
        
    def move_steps(self, steps, direction):
        gpio.output(self.dir_pin, direction)
        for _ in range(steps):
            state = gpio.input(self.limit_pin)
            if state == gpio.LOW:
                time.sleep(2)
                self.move_left(400)
            
            gpio.output(self.step_pin, gpio.HIGH)
            time.sleep(self.delay)
            gpio.output(self.step_pin, gpio.LOW)
            time.sleep(self.delay)
            
    def move_left(self, steps):
        self.move_steps(steps, self.ccw)
        
    def move_right(self, steps):
        self.move_steps(steps, self.cw)
        
    def cleanup(self):
        gpio.cleanup()
