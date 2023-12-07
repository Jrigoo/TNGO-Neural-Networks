import RPi.GPIO as GPIO
import time

class Motor:
    def __init__(self,stepper_velocity=0.005):
        GPIO.setmode(GPIO.BOARD)

        #  Set Servo Motor
        GPIO.setup(32,GPIO.OUT)
        self.servo = GPIO.PWM(32,50) 
        self.servo.start(0)

        self.__direction_pin = 38
        self.__step_pin = 40
        self.__limit_pin = 8

        # Set Stepper Motor
        GPIO.setup(self.__direction_pin, GPIO.OUT) # Direction
        GPIO.setup(self.__step_pin, GPIO.OUT) # Step
        GPIO.setup(self.__limit_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Limit
        self.stepper_velocity = stepper_velocity

    def __move_servo(self,angle):
        self.servo.ChangeDutyCycle(2+(angle/18))
        time.sleep(1)
        self.servo.ChangeDutyCycle(0)

    def __move_stepper(self,steps:int,direction:int):
        GPIO.output(self.__direction_pin, direction)
        for _ in range(steps):
            GPIO.output(self.__step_pin, GPIO.HIGH)
            time.sleep(self.stepper_velocity)
            GPIO.output(self.__step_pin, GPIO.LOW)
            time.sleep(self.stepper_velocity)

    def classify_trash(self,type):
        types = {
            "lata":[(200,1),(200,0)],
            "basura":[(200,0),(200,1)],
            "plastico":[(400,0),(400,1)],
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
    motor = Motor(0.001)
    try:
        while True:
            tipo = input("Desecho: basura, lata, papel, plastico: ")    
            motor.classify_trash(tipo)
    except Exception as e:
        print("Done")
    finally:
	    motor.cleanup_pins()
