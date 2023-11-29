import pyaudio
import numpy as np
from scipy import signal
from model.neural_networks import AudioNeuralNetwork
from control.hardware import Motor, ColorSensor
import time
import cv2

trash_audio_model = AudioNeuralNetwork("model/tf_lite/trash-audio-model-v3.0.lite")

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

try:
    motor = Motor()
    color_sensor = ColorSensor()
    while True:
        # Audio data
        audio_data = stream.read(CHUNK, exception_on_overflow=False)
        audio_classification = trash_audio_model.run(audio_data)
        color_avg = color_sensor.color_state()

        print(f"Audio: {audio_classification} Color: {color_avg}")
        time.sleep(0.1)

except:
    print("done.")
finally:
    motor.cleanup_pins()
    stream.stop_stream()
    stream.close()
    p.terminate()

