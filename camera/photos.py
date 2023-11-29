import cv2
import time

#find -name "*.png" -type f -delete

i = 0
type = "papel"

try:
    cap = cv2.VideoCapture(0)
    while i < 100:  # Cambiado a 100 ya que generalmente queremos 100 imágenes, no 101
        ret, frame = cap.read()

        if ret:
            frame = cv2.convertScaleAbs(frame, alpha=1, beta=1)
            cv2.imwrite(f'{type}.{i}.png', frame)
            i += 1
            print("papel",i)
            time.sleep(0.05)

finally:
    cap.release()  # Liberar recursos de la cámara al finalizar
    cv2.destroyAllWindows()  # Cerrar todas las ventanas de OpenCV

print("Captura completada.")
