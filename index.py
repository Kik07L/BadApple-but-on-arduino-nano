import cv2
import serial
import time
from PIL import Image

# Initialiser la connexion Serial avec Arduino
ser = serial.Serial('COM5', 115200)  # Remplacez 'COM5' par le port correct de votre Arduino
time.sleep(2)  # Attendre l'initialisation

# Paramètres de la vidéo
video_path = "bad_apple.mp4"  # Chemin vers la vidéo MP4
block_size = 8
width = 128
height = 64

def send_block(x, y, block_data):
    """Envoie les données d'un bloc (8x8 pixels) à l'Arduino"""
    ser.write(bytearray([x, y]))  # Envoyer la position x et y
    ser.write(bytearray(block_data))  # Envoyer les données du bloc
    time.sleep(0.005)  # Petite pause pour éviter la surcharge du buffer série (ajustée pour plus de rapidité)

def compare_and_send(image1, image2):
    """Compare deux images et envoie seulement les blocs 8x8 qui changent"""
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            # Extraire le bloc 8x8 pixels des deux images
            block1 = [image1.getpixel((x + j, y + i)) for i in range(block_size) for j in range(block_size)]
            block2 = [image2.getpixel((x + j, y + i)) for i in range(block_size) for j in range(block_size)]
            
            if block1 != block2:  # Si le bloc a changé, on l'envoie
                block_data = []
                for i in range(block_size):
                    byte = 0
                    for j in range(block_size):
                        if block2[i * block_size + j] == 0:  # Noir = 1, Blanc = 0
                            byte |= (1 << (block_size - 1 - j))  # Inverser l'ordre des bits
                    block_data.append(byte)
                send_block(x, y, block_data)

def process_video(video_path):
    """Lit la vidéo et traite chaque frame pour l'envoyer à l'Arduino"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erreur : Impossible de lire la vidéo.")
        return
    
    ret, frame = cap.read()  # Lire la première frame
    previous_image = None

    while ret:
        # Redimensionner la frame à 128x64 et la convertir en niveaux de gris
        frame_resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
        _, frame_bw = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY)  # Convertir en noir et blanc

        # Convertir la frame en image Pillow pour faciliter le traitement des pixels
        current_image = Image.fromarray(frame_bw).convert('1')  # 1 bit par pixel

        if previous_image is not None:
            compare_and_send(previous_image, current_image)  # Comparer avec la frame précédente et envoyer les blocs modifiés

        previous_image = current_image  # Stocker la frame actuelle pour la prochaine comparaison

        # Lire la frame suivante
        ret, frame = cap.read()

        # Petite pause pour la synchronisation (~25 FPS)
        time.sleep(0.04)

    cap.release()

# Lancer le traitement de la vidéo
process_video(video_path)

# Fermer la connexion Serial une fois terminé
ser.close()
