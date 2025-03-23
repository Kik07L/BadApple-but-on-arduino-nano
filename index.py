import cv2
import serial
import time
from PIL import Image


ser = serial.Serial('COM4', 115200)  # Replace 'COM5' by the "COM" thing ur arduino is using
time.sleep(2)  


video_path = "bad_apple.mp4"  # video path
block_size = 8
width = 128
height = 64

def send_block(x, y, block_data):
    """sends data"""
    ser.write(bytearray([x, y]))  
    ser.write(bytearray(block_data))  
    time.sleep(0.005) 

def compare_and_send(image1, image2):
    """Compare images"""
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            
            block1 = [image1.getpixel((x + j, y + i)) for i in range(block_size) for j in range(block_size)]
            block2 = [image2.getpixel((x + j, y + i)) for i in range(block_size) for j in range(block_size)]
            
            if block1 != block2:  
                block_data = []
                for i in range(block_size):
                    byte = 0
                    for j in range(block_size):
                        if block2[i * block_size + j] == 0:  # black = 1, white = 0
                            byte |= (1 << (block_size - 1 - j))  
                    block_data.append(byte)
                send_block(x, y, block_data)

def process_video(video_path):
    """frame processing"""
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error : can't read the video... maybe you don't have a bad apple ? ")
        return
    
    ret, frame = cap.read()  
    previous_image = None

    while ret:
        
        frame_resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        frame_gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY) # processing the b&w thing for no color bugs or type of strenge thing
        _, frame_bw = cv2.threshold(frame_gray, 128, 255, cv2.THRESH_BINARY)  

        
        current_image = Image.fromarray(frame_bw).convert('1')  

        if previous_image is not None:
            compare_and_send(previous_image, current_image)  

        previous_image = current_image  

        
        ret, frame = cap.read()

        
        time.sleep(0.04)

    cap.release()


process_video(video_path)

ser.close()
