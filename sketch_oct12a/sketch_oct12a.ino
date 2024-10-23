#include <Adafruit_GFX.h>        // Bibliothèque de base pour le rendu graphique
#include <Adafruit_SH110X.h>     // Bibliothèque pour le SH110X
#include <Wire.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define BLOCK_SIZE 8

Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1); // -1 pour pas de reset

void setup() {
  Serial.begin(115200);  // Initialisation de la communication Serial
  Wire.setClock(400000);  // Passer l'I2C en mode rapide à 400kHz
  display.begin();       // Initialisation de l'écran OLED
  display.clearDisplay(); // Nettoyer l'écran
  display.display();      // Afficher l'écran vide
}

void loop() {
  if (Serial.available() >= (BLOCK_SIZE + 2)) {
    // Lire la position du bloc
    uint8_t x = Serial.read();   // Lire la position x
    uint8_t y = Serial.read();   // Lire la position y

    // Vérification des limites de l'écran
    if (x >= SCREEN_WIDTH || y >= SCREEN_HEIGHT) {
      return; // Sortir si la position est hors limites
    }

    uint8_t data[BLOCK_SIZE];    // Stocker les données du bloc 8x8 pixels

    // Lire les données du bloc (8 octets pour un bloc de 8x8 pixels)
    for (int i = 0; i < BLOCK_SIZE; i++) {
      if (Serial.available() > 0) {
        data[i] = Serial.read();
      }
    }

    // Inversion horizontale des blocs
    int mirrored_x = SCREEN_WIDTH - x - BLOCK_SIZE;  // Calculer la position inversée du bloc sur l'axe X

    // Dessiner le bloc à la position inversée (mirrored_x, y) sur l'écran
    for (int i = 0; i < BLOCK_SIZE; i++) {
      for (int j = 0; j < BLOCK_SIZE; j++) {
        if (data[i] & (1 << j)) {  // Si le bit est à 1, on dessine un pixel blanc
          display.drawPixel(mirrored_x + j, y + i, SH110X_WHITE);  // Dessiner un pixel allumé (blanc)
        } else {  // Sinon on dessine un pixel noir pour l'effacer
          display.drawPixel(mirrored_x + j, y + i, SH110X_BLACK);  // Effacer le pixel (dessiner en noir)
        }
      }
    }
  }

  // Afficher l'écran après avoir reçu et traité tous les blocs
  display.display();  // Appeler display.display() une seule fois par frame complète
}
