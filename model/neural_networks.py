from processing.mfe import generate_features as audio_features
from processing.image import generate_features as image_features
import tflite_runtime.interpreter as tflite
from scipy import signal
import numpy as np
import cv2

class NeuralNetwork:
    def __init__(self, model_path):
        self.interpreter, self.input_model, self.output_model = self.__init_model(
            model_path)

    def __init_model(self, path):
        try:
            interpreter = tflite.Interpreter(model_path=path)
            interpreter.allocate_tensors()
            input = interpreter.get_input_details()  # Lo que recibe
            output = interpreter.get_output_details()  # Lo que retorna
            return interpreter, input, output
        except:
            print("Modelo no cargado correctamente")

    def softmax(self, x):
        exp_x = np.exp(x - np.max(x))
        return exp_x / exp_x.sum(axis=-1, keepdims=True)


class AudioNeuralNetwork(NeuralNetwork):
    def __preprocessing(self, raw_data):
        raw_data = np.frombuffer(raw_data, dtype=np.int16)
        raw_data = signal.resample(raw_data, int(len(raw_data) * (16000 / 44100)))

        # Resize audio signal
        if len(raw_data) != 6800:
            raw_data = np.resize(raw_data, 6800)
        
        raw_data = np.array(raw_data, dtype=np.float32)

        implementation_version = 4  # 4 is latest versions
        draw_graphs = False  # For testing from script, disable graphing to improve speed
        axes = ['accY']
        sampling_freq = 16000

        # Set the desired settings/params
        frame_length = 0.02
        frame_stride = 0.01
        num_filters = 40
        fft_length = 256
        low_frequency = 0
        high_frequency = 0
        noise_floor_db = -52
        preprocessing = audio_features(implementation_version, draw_graphs, raw_data, axes, sampling_freq, frame_length,
                                          frame_stride, num_filters, fft_length, low_frequency, high_frequency, 0, noise_floor_db)
        return np.array(preprocessing['features'], dtype=np.float32)

    def run(self, raw_data):
        # Obtenemos los features y añadimos una dimensión extra
        # El shape del model debe ser: (1, 1640)
        self.features = np.expand_dims(self.__preprocessing(raw_data), axis=0)
        self.interpreter.set_tensor(
            self.input_model[0]['index'], self.features)
        self.interpreter.invoke()  # Corremos la inferencia

        result = self.interpreter.get_tensor(self.output_model[0]['index'])
        res_probs = self.softmax(result) 
        res_probs = np.insert(res_probs,2,0) # añadimos un valor cero que representa papel
        
        idx = np.argmax(res_probs)
        items = ["lata","nada","papel","plastico"]
        return items[idx],res_probs


class ImageNeuralNetwork(NeuralNetwork):
    def __preprocessing(self,raw_data):
        raw_data = cv2.rotate(raw_data,cv2.ROTATE_180)
        raw_image = cv2.resize(raw_data,(96,96))
        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
        raw_image = raw_image.flatten()

        repeated_arr = np.repeat(raw_image, 3)
        featured = np.around(np.insert(repeated_arr, np.arange(3, len(repeated_arr) + 1, 3), 0),0)
        return np.array(image_features(1, False, featured, "Grayscale")["features"],dtype=np.float32)

    def run(self, raw_data):
        self.features = self.__preprocessing(raw_data)
        self.features = np.reshape(self.features,(1,96,96,1)) # El input shape debe ser (1,96,96,1)

        self.interpreter.set_tensor(self.input_model[0]['index'], self.features)
        self.interpreter.invoke() 
        result = self.interpreter.get_tensor(self.output_model[0]['index'])
        res_probs = self.softmax(result) 

        idx = np.argmax(res_probs)
        items = ["lata","nada","papel","plastico"]
        return items[idx],res_probs
