
import librosa
import numpy as np
import scipy.io.wavfile
import os


def chop_sample(ruta_archivo, directorio_salida, sample_type, default_idx):
    # Cargar el archivo de audio
    duracion_segmento = 0.425
    umbral = 0.5
    audio, _ = librosa.load(ruta_archivo, sr=None)

    # Encontrar los transientes utilizando la función onset_detect
    transientes = librosa.onset.onset_detect(
        y=audio, sr=librosa.get_samplerate(ruta_archivo), units='time', backtrack=True)

    # Calcular la duración en muestras de cada segmento
    duracion_muestras = int(
        duracion_segmento * librosa.get_samplerate(ruta_archivo))

    # Iterar sobre los transientes y cortar el audio en segmentos de 425ms
    for i, transiente in enumerate(transientes):
        inicio = max(0, int(transiente * librosa.get_samplerate(ruta_archivo)))
        fin = min(inicio + duracion_muestras, len(audio))
        segmento = audio[inicio:fin]

        if np.max(np.abs(segmento)) > umbral:
            nombre_archivo = f"{directorio_salida}/{sample_type}.{default_idx}_{i + 1}.wav"
            fs = librosa.get_samplerate(ruta_archivo)
            scipy.io.wavfile.write(nombre_archivo, fs, segmento)


if __name__ == "__main__":
    """ 
    1. Debo abrir la carpeta de training y testing
    2. Debo obtener la ruta de cada sample
    3. Debo guardar cada sample con su label + el # de sample como .wav
    """
    directory = "chops"
    file_paths = []
    for (dirpath, dirnames, filenames) in os.walk(directory):
        file_paths.extend(filenames)

    # Chopeamos cada file
    for i in range(len(file_paths)):
        ruta_archivo = f'{directory}/{file_paths[i]}'
        sample_type = ruta_archivo.split(".")[0].split("/")[1]
        chop_sample(ruta_archivo, f"new_{directory}", sample_type, i)
