import pyaudio
import numpy as np
from scipy import signal
from model.neural_networks import AudioNeuralNetwork,ImageNeuralNetwork
from control.hardware import Motor, ColorSensor
import time
import cv2

trash_img_model = ImageNeuralNetwork("model/tf_lite/trash-img-model-v2.0.lite")

# Open camera
cap = cv2.VideoCapture(0)

try:
    motor = Motor()
    color_sensor = ColorSensor()
    while True:
        ret, frame = cap.read()
        if ret:
            # Image data
            frame = cv2.convertScaleAbs(frame, alpha=1, beta=1)
            image_classification = trash_img_model.run(frame)
            color_avg = color_sensor.color_state()
            print(f"Image: {image_classification} Color Sensor: {color_avg}")
            time.sleep(0.05)
except Exception as e:
    print(e)
finally:
    cap.release() 
    cv2.destroyAllWindows()
    motor.cleanup_pins()

