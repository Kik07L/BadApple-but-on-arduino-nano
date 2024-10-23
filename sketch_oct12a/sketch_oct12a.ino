#include <Adafruit_GFX.h>        
#include <Adafruit_SH110X.h>     
#include <Wire.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define BLOCK_SIZE 8

Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1); // WARNING !!! this code is made for SH1106G displays ( oled small display that u can found on aliexpress) if u have a SH1107 change the  Adafruit_SH1106G thing by Adafruit_SH1107

void setup() {
  Serial.begin(115200);  
  Wire.setClock(400000);  
  display.begin();       
  display.clearDisplay(); 
  display.display();      
}

void loop() {
  if (Serial.available() >= (BLOCK_SIZE + 2)) {
    
    uint8_t x = Serial.read();   
    uint8_t y = Serial.read();   

    
    if (x >= SCREEN_WIDTH || y >= SCREEN_HEIGHT) {
      return; 
    }

    uint8_t data[BLOCK_SIZE]; 

    
    for (int i = 0; i < BLOCK_SIZE; i++) {
      if (Serial.available() > 0) {
        data[i] = Serial.read();
      }
    }

    
    int mirrored_x = SCREEN_WIDTH - x - BLOCK_SIZE;  

    
    for (int i = 0; i < BLOCK_SIZE; i++) {
      for (int j = 0; j < BLOCK_SIZE; j++) {
        if (data[i] & (1 << j)) {  
          display.drawPixel(mirrored_x + j, y + i, SH110X_WHITE);  
        } else { 
          display.drawPixel(mirrored_x + j, y + i, SH110X_BLACK);  
        }
      }
    }
  }

  
  display.display();  
}
