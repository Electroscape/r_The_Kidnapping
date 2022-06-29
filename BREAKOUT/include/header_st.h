/**
* To configure a relay:
*   - rename REL_X_PIN to informative name
*   - rename and set REL_X_INIT with your init value
*   - create array with the used pins and benefit from loops :D
*/
#pragma once

const unsigned long rfidCheckInterval = 250;

#define RFID_AMOUNT         1

const uint8_t keya[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };

#define RFID_DATABLOCK      1
#define OLED_I2C_ADD 0x3C    // Ist durch Hardware des OLEDs vorgegeben


// --- RFID settings ---

// define the pins for SPI communication. this may move to std lib
#define PN532_SCK               13
#define PN532_MOSI              11
#define PN532_MISO              12

#define RFID_1_SS_PIN           8     /* Per Konvention ist dies RFID-Port 1                                */
#define RFID_2_SS_PIN           7     /* Per Konvention ist dies RFID-Port 2                                */
#define RFID_3_SS_PIN           4     /* Per Konvention ist dies RFID-Port 3                                */
#define RFID_4_SS_PIN           2     /* Per Konvention ist dies RFID-Port 4                                */

const byte RFID_SSPins[]  = {RFID_1_SS_PIN};

// --- LED settings --- 
#define NR_OF_LEDS             31  /* Anzahl der Pixel auf einem Strang (Test 1 Pixel)                   */
#define STRIPE_CNT             1

#define RFID_1_LED_PIN          9     /* Per Konvention ist dies RFID-Port 1                                */
#define RFID_2_LED_PIN          6     /* Per Konvention ist dies RFID-Port 2                                */
#define RFID_3_LED_PIN          5     /* Per Konvention ist dies RFID-Port 3                                */
#define RFID_4_LED_PIN          3     /* Per Konvention ist dies RFID-Port 4   */

// 140cm of 60 leds/m = 84 Leds to be safe bump it to 100
int ledCnts[STRIPE_CNT] = {100};
int ledPins[STRIPE_CNT] = {RFID_1_LED_PIN};
