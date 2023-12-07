import pyaudio
import numpy as np
from model.neural_networks import AudioNeuralNetwork,ImageNeuralNetwork
from control.hardware import Motor, ColorSensor
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
try:
    motor = Motor(0.002)
    color_sensor = ColorSensor()

    while True:
        ret, frame = cap.read()
        image_result = "nada"

        # Audio data
        audio_data = stream.read(CHUNK, exception_on_overflow=False)
        audio_result,audio_probs = trash_audio_model.run(audio_data)
        color_avg = color_sensor.color_state()

        print(f"audio: {audio_result} color: {color_avg}")        
        if audio_result != "nada": 
            print(f"audio captado... {audio_result}")
            start_time = time.time()
            while color_avg > 35:
                if time.time() - start_time > 0.5:
                    break

        if color_avg < 35:
            frame_counter = 0
            start_time = time.time()
            while frame_counter < 5:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.convertScaleAbs(frame, alpha=1, beta=1)
                    image_result,image_probs = trash_img_model.run(frame)
                    frame_counter += 1
            if  image_result != "nada":
                print(f"Image: {image_result} Audio: {audio_result}")
                motor.classify_trash(image_result)
                  
        time.sleep(0.05)

except:
    print("done.")
finally:
    cap.release() 
    cv2.destroyAllWindows()
    motor.cleanup_pins()
    stream.stop_stream()
    stream.close()
    p.terminate()

