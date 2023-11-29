import pyaudio
import numpy as np
from scipy import signal
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
    motor = Motor()
    color_sensor = ColorSensor()
    while True:
        ret, frame = cap.read()
        if ret:
            # Image data
            frame = cv2.convertScaleAbs(frame, alpha=1, beta=1)
            cv2.imshow("frame",frame)
            image_classification = trash_img_model.run(frame)

            # Audio data
            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_44 = np.frombuffer(audio_data, dtype=np.int16)
            audio_16 = signal.resample(audio_44, int(len(audio_44) * (16000 / 44100)))

            # Resize audio signal
            if len(audio_16) != CHUNK:
                audio_16 = np.resize(audio_16, CHUNK)
            
            audio_classification = trash_audio_model.run(np.array(audio_16, dtype=np.float32))
            color_avg = color_sensor.color_state()

            print(f"Audio: {audio_classification} Image: {image_classification} Color: {color_avg}")

            
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break
            time.sleep(0.1)

except:
    print("done.")
finally:
    cap.release() 
    cv2.destroyAllWindows()
    motor.cleanup_pins()
    stream.stop_stream()
    stream.close()
    p.terminate()

