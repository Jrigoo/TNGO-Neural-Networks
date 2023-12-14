import RPi.GPIO as GPIO
import time

class Motor:
    def __init__(self,step_delay=0.01):
        GPIO.setmode(GPIO.BOARD)

        #  Set Servo Motor
        GPIO.setup(32,GPIO.OUT)
        self.servo = GPIO.PWM(32,50) 
        self.servo.start(0)

        # Set Stepper Motor
        self.__A = 8
        self.__C = 10
        self.__B = 12
        self.__D = 16

        GPIO.setup(self.__A, GPIO.OUT)
        GPIO.setup(self.__C, GPIO.OUT)
        GPIO.setup(self.__B, GPIO.OUT)
        GPIO.setup(self.__D, GPIO.OUT)

        self.__step_sequence = [
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 0, 1],
            [1, 0, 0, 1]
        ]

        self.step_delay = step_delay

    def __move_servo(self,angle):
        self.servo.ChangeDutyCycle(2+(angle/18))
        time.sleep(1)
        self.servo.ChangeDutyCycle(0)

    def __move_stepper(self,steps:int,direction:int):
        steps_left = steps
        last_step_time = 0
        step_number = 0

        while steps_left > 0:
            now = time.time()
            if (now - last_step_time) >= self.step_delay:
                last_step_time = now
                if direction == 1:
                    step_number += 1
                    if step_number == 4:
                        step_number = 0
                else:
                    if step_number == 0:
                        step_number = 4
                    step_number -= 1
                steps_left -= 1

                step = step_number % 4
                GPIO.output(self.__A, self.__step_sequence[step][0])
                GPIO.output(self.__C, self.__step_sequence[step][1])
                GPIO.output(self.__B, self.__step_sequence[step][2])
                GPIO.output(self.__D, self.__step_sequence[step][3])

    def classify_trash(self,type):
        types = {
            "lata":[(100,1),(100,0)],
            "basura":[(100,0),(100,1)],
            "plastico":[(200,0),(200,1)],
            "papel":[(0,0),(0,0)]
        }

        if type in types.keys():
            self.__move_stepper(types[type][0][0], types[type][0][1])
            self.__open_gate()
            self.__move_stepper(types[type][1][0], types[type][1][1])

    def __open_gate(self):
        self.__move_servo(108)
        time.sleep(2)
        self.__move_servo(178)

    def cleanup_pins(self):   
        self.servo.stop()
        GPIO.cleanup()


class ColorSensor:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)

        self.__S3 = 11
        self.__S2 = 13
        self.__OUT = 15

        GPIO.setup(self.__OUT,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.__S2,GPIO.OUT)
        GPIO.setup(self.__S3,GPIO.OUT)


    def __pulseIn(self,pin:int, timeout:float=1) -> float:
        """ 
        Espera que el pin pase de HIGH to LOW, Empieza temporizador, 
        Espera que el pin pase de LOW a HIGH, Detiene el temporizador

        args:
            pin: OUT pin
            timeout: Tiempo de espera. Default 1seg
        
        returns:
            pulse_duration: Duración del pulso en microsegundos
        """
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

    def color_state(self):
        # Red color detection
        GPIO.output(self.__S2,GPIO.LOW)
        GPIO.output(self.__S3,GPIO.LOW)
        red = round(self.__pulseIn(self.__OUT),3)

        # Green
        GPIO.output(self.__S2,GPIO.HIGH)
        GPIO.output(self.__S3,GPIO.HIGH)
        green = round(self.__pulseIn(self.__OUT),3)

        # Blue
        GPIO.output(self.__S2,GPIO.LOW)
        GPIO.output(self.__S3,GPIO.HIGH)
        blue = round(self.__pulseIn(self.__OUT),3)

        average_value = round((red + green + blue)/3,2)
        return average_value
    

if __name__ == "__main__":
    motor = Motor(0.005)
    try:
        while True:
            tipo = input("Desecho: basura, lata, papel, plastico: ")    
            motor.classify_trash(tipo)
    except Exception as e:
        print("Done")
    finally:
	    motor.cleanup_pins()
