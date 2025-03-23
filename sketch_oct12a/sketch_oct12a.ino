#include <Adafruit_GFX.h>        
#include <Adafruit_SH110X.h>     
#include <Wire.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define BLOCK_SIZE 8

Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1); 

void setup() {
  Serial.begin(500000);  
  Wire.setClock(400000);  
  display.begin();       
  display.clearDisplay(); 
  display.display();      
}

void loop() {
  if (Serial.available() >= (BLOCK_SIZE + 2)) {
    uint8_t x = Serial.read();   
    uint8_t y = Serial.read();   

    // Check if coordinates are within screen bounds
    if (x >= SCREEN_WIDTH || y >= SCREEN_HEIGHT) {
      return; 
    }

    uint8_t data[BLOCK_SIZE]; 
    for (int i = 0; i < BLOCK_SIZE; i++) {
      if (Serial.available() > 0) {
        data[i] = Serial.read();
      }
    }

    // Ensure the block fits within the screen
    int mirrored_x = SCREEN_WIDTH - x - BLOCK_SIZE;  

    // Draw the block of pixels
    for (int i = 0; i < BLOCK_SIZE; i++) {
      for (int j = 0; j < BLOCK_SIZE; j++) {
        bool pixel = data[i] & (1 << j);
        // Inverser la logique des couleurs ici : on dessine en noir pour 1 et en blanc pour 0
        display.drawPixel(mirrored_x + j, y + i, pixel ? SH110X_BLACK : SH110X_WHITE); 
      }
    }
    display.display();  
  }
}
