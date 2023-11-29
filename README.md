# TNGO
El TNGO es un basurero autónomo que te permite reciclar desechos. Para la primera versión, el prototipo es capaz de clasificar papeles, latas y botellas de plastico. El dispositivo utiliza redes neuronales de audio e imagen para la clasificación correcta de los desechos. En caso tal de que no sea definido el desecho a clasificar correctamente, el basurero dispondrá el desecho en un compartimento por default

## Estructura
La estructura de los folders es la siguiente:
```
 ./
 |-- audio
	|-- audio_chop.py
|-- camera
	|-- check_scale.py
	|-- photo.py
|-- control
    |-- __init__.py
    |-- color.py 
    |-- hardware.py
    |-- servo.py
    |-- stepper.py
|-- model
    |-- tf_lite
    |-- neural_networks.py
|-- processing
|-- main.py
|-- audio_only.py
|-- image_only.py
|-- threads.py

```
1. `audio` es una carpeta que posee un código en python que agarra archivos *.wav de audio de 16kHZ de una carpeta llamada `chops`, obtiene las muestras más significativas de los mismos y las guarda en samples de 425ms en una carpeta llamada `new_chops`. Este código se utilizó para generar la data para el entrenamiento de la red neuronal de clasificación de audio
2. `camara` es una carpeta que posee 2 archivos:
    - `check_scale.py` es un código utilizado para ajustar los factores beta y alpha de la camara. Esto dado a que la camara no tiene mucha iluminación, por lo tanto era necesario ajustarla
    - `photos.py` es un código utilizado para tomar 100 fotos segun el label deseado. Se utilizó para generar la data para el entrenamiento de la red neuronal de clasificación de imagenes
3. `control` es una carpeta con varios archivos y clases para el control de los sensores y motores
    - `color.py` posee un código para utilizar y leer data de un sensor de color TCS230/TCS3200
    - `servo.py` posee un código para controlar un motor servo MG995 y brindar direcciones de los angulos deseados
    - `hardware.py` consite en 2 clases utilizadas para el control y lectura de los motores y sensores.
        - `Motor` es una clase utilizada para incializar y controlar el motor servo y el motor paso a paso. La misma está diseñada para la clasificación correcta de los desechos
        - `ColorSensor` es una clase utilizada para incializar y utilizar el sensor de color TCS230/TCS3200. El sensor de color, suele tener variaciones menores al valor de 35 (aproximadamente) cuando detecta un objeto. Por lo tanto, aprovechando estas variaciones, definimos la existencia de un desecho cuando esto sucede
4. `model` posee todo el código y modelos relacionados a las redes neuronales
    - `tf_lite` es una carpeta que posee diferences archivos con modelos de .tflite
    - `neural_networks.py` posee 3 clases utilizadas para cargar los modelos de tflite
        - `NeuralNetwork` es una clase general que inicializa el modelo del archivo de tf_lite, también inicializa los inputs, outputs y el interpreter. Por último tiene una función softmax, dado a que para estos ejemplos de clasificación es la que se utiliza  
        - `AudioNeuralNetwork` es una clase que inicializa la red neuronal de audio. Es una clase hija de la clase padre `NeuralNetwork`, por lo tanto hereda todos los atributos y métodos previamente mencionados. Esta clase tiene 2 métodos extras, uno dedicado el procesamiento del audio y otro a la ejecución del modelo de clasificación. La red neuronal de audio capta muestras de 16kHZ con chunks de 6800 (equivalente a 425ms) para clasificar. El audio se captura en una Frecuencia de Muestreo (RATE) de 44100Hz dado a que esa es la frecuencia default del micrófono. Por lo tanto se realiza una conversión de 44100 Hz a 16000 Hz cómo un procesamiento extra

        - `ImageNeuralNetwork` es una clase que inicializa la red neuronal de imagenes. Es una clase hija de la clase padre `NeuralNetwork`, por lo tanto hereda todos los atributos y métodos previamente mencionados. Esta clase tiene 2 métodos extras, uno dedicado el procesamiento de las imagenes y otro a la ejecución del modelo de clasificación. La red neuronal de imagenes capta frames de 96x96 pixeles en escala de grises. Las imagenes también tienen un aumento en los factores beta y alpha para mayor brillo.

5. `preprocessing` es una carpeta que posee bloques de procesamiento brindados por edge impulse. Los bloques se encuentran en el siguiente [repositorio](https://github.com/edgeimpulse/processing-blocks) de github.
6. `main.py` es el código que combina las redes neuronales junto con los sensores y motores. Es el código principal que define el funcionamiento del TNGO
7. `audio_only.py` es un código que se enfoca en ejecutar el TNGO utilizando únicamente la red neuronal de audio. Es utilizado para pruebas
8. `image_only.py` es un código que se enfoca en ejecutar el TNGO utilizando únicamente la red neuronal de imagen. Es utilizado para pruebas
9. `threads.py` es el código que combina las redes neuronales junto con los sensores y motores. Es similar al código de `main.py`, la única diferencia es que utiliza threads para la ejecución independiente de cada red neuronal
