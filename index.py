import cv2
import serial
import time
from PIL import Image

ser = serial.Serial('COM4', 500000)  # Remplacez 'COM4' par le port série de votre Arduino
time.sleep(2)

video_path = "bad_apple.mp4"  # Chemin de la vidéo
block_size = 8
width = 128
height = 64

def send_block(x, y, block_data):
    """Envoie les données d'un bloc"""
    ser.write(bytearray([x, y]))  # Envoi de la position du bloc
    ser.write(bytearray(block_data))  # Envoi des données du bloc
    time.sleep(0.005)  # Légère pause pour éviter la surcharge du buffer série

def compare_and_send(image1, image2):
    """Compare deux images et envoie les blocs modifiés"""
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            
            block1 = [image1.getdata()[i * width + j] for i in range(y, y + block_size) for j in range(x, x + block_size)]
            block2 = [image2.getdata()[i * width + j] for i in range(y, y + block_size) for j in range(x, x + block_size)]
            
            if block1 != block2:  
                block_data = []
                for i in range(block_size):
                    byte = 0
                    for j in range(block_size):
                        if block2[i * block_size + j] == 0:  # 0 = noir, 1 = blanc
                            byte |= (1 << (block_size - 1 - j))  
                    block_data.append(byte)
                send_block(x, y, block_data)

def process_video(video_path):
    """Traitement de la vidéo et envoi des images"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erreur : Impossible de lire la vidéo.")
        return
    
    ret, frame = cap.read()  
    previous_image = None

    while ret:
        
        frame_resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)  # Conversion en niveau de gris
        _, frame_bw = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY)  # Seuillage pour obtenir l'image binaire

        current_image = Image.fromarray(frame_bw).convert('1')  # Conversion en image binaire

        if previous_image is not None:
            compare_and_send(previous_image, current_image)  # Comparaison et envoi des blocs modifiés

        previous_image = current_image  

        ret, frame = cap.read()

        time.sleep(0.04)  # Pause pour correspondre à la fréquence d'image de la vidéo (25 FPS)

    cap.release()

process_video(video_path)

ser.close()
