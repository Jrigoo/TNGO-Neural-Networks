import cv2
import time

cv2.namedWindow("Slider")
cv2.resizeWindow("Slider",240,500)
cv2.createTrackbar("Alpha","Slider",1,50, lambda e: e)
cv2.createTrackbar("Beta","Slider",1,50, lambda e: e)

try:
    cap = cv2.VideoCapture(0)
    while cap.isOpened(): 
        ret, frame = cap.read()

        beta = cv2.getTrackbarPos("Beta","Slider")
        alpha = cv2.getTrackbarPos("Alpha","Slider")

        if ret:
            frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
            cv2.imshow("type", frame)


            key = cv2.waitKey(1)
            if key == ord('q'):
                break

            time.sleep(0.1)  # Añadir un pequeño retardo entre capturas para evitar problemas

finally:
    cap.release()  # Liberar recursos de la cámara al finalizar
    cv2.destroyAllWindows()  # Cerrar todas las ventanas de OpenCV

print("Captura completada.")
