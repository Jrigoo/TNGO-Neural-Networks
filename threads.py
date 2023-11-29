import pyaudio
import numpy as np
from scipy import signal
from model.neural_networks import AudioNeuralNetwork,ImageNeuralNetwork
from control.hardware import Motor, ColorSensor
import threading
import time
import cv2

trash_audio_model = AudioNeuralNetwork("model/tf_lite/trash-audio-model-v3.0.lite")
trash_img_model = ImageNeuralNetwork("model/tf_lite/trash-img-model-v2.0.lite")

# Define Microphone parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 6800

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=CHUNK)

# Open camera
cap = cv2.VideoCapture(0)
motor = Motor()
color_sensor = ColorSensor()

# Initialize results
audio_classification = "Nada"
image_classification = "Nada"

def camara_processing(_, run_event):
    global image_classification
    while run_event.is_set():
        ret, frame = cap.read()
        if ret:
            frame = cv2.convertScaleAbs(frame, alpha=1, beta=1)
            image_classification = trash_img_model.run(frame)


def audio_processing(_, run_event):
    global audio_classification
    while run_event.is_set():
        audio_data = stream.read(CHUNK, exception_on_overflow=False)
        audio_classification = trash_audio_model.run(audio_data)


run_event = threading.Event()
run_event.set()
t_audio = threading.Thread(
    target=audio_processing, args=("Audio", run_event))
t_image = threading.Thread(
    target=camara_processing, args=("Image", run_event))
t_audio.start()
t_image.start()

try:
    while True:
        color_avg = color_sensor.color_state()
        print("Image: {} Audio: {} Color: {}".format(image_classification,audio_classification,color_avg))
        time.sleep(0.1)
                

except:
    print("done.")
finally:    
    run_event.clear()
    t_audio.join()
    t_image.join()
    cap.release() 
    cv2.destroyAllWindows()
    motor.cleanup_pins()
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("threads successfully closed")
