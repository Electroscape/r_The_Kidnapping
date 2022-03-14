/**
* To configure a relay:
*   - rename REL_X_PIN to informative name
*   - rename and set REL_X_INIT with your init value
*   - create array with the used pins and benefit from loops :D
*/
#pragma once

String title = "ENT_HH_BREAKOUT";
String versionDate = "13.03.2022";
String version = "version 1.1 HH";
// String brainName = String("BrCOLOR");
// String relayCode = String("HID");
const unsigned long heartbeatFrequency = 5000;


// #define DEBUGMODE           1
#define RESET_DURATION      12
#define RFID_TICKS_REQUIRED 3

#define RFID_AMOUNT         1
#define RFID_SOLUTION_SIZE  4

const uint8_t keya[6] = { 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF };
const char RFID_solutions[1][RFID_SOLUTION_SIZE]  = {"AH"};

#define RFID_DATABLOCK      1

// by default enabled
//#define OLED_DISABLE 1

// Standards der Adressierung (Konvention)
// this is optional now due to default value in STB lib
// #define RELAY_I2C_ADD 0x3F   // Relay Expander																							*/
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

// the black ones with 30/meter actually have segments of 3 leds per IC
#define NR_OF_LEDS             31  /* Anzahl der Pixel auf einem Strang (Test 1 Pixel)                   */
// BE CAREFUL WHEN SETTING ALL LEDS to a colour use the socket count for this
#define STRIPE_CNT             1
#define LED_STRIP_TYPE         WS2811
#define COLOR_ORDER            BRG // BRG

#define RFID_1_LED_PIN          9     /* Per Konvention ist dies RFID-Port 1                                */
#define RFID_2_LED_PIN          6     /* Per Konvention ist dies RFID-Port 2                                */
#define RFID_3_LED_PIN          5     /* Per Konvention ist dies RFID-Port 3                                */
#define RFID_4_LED_PIN          3     /* Per Konvention ist dies RFID-Port 4   */

#define REL_AMOUNT 1

enum REL_PIN {
    REL_DOOR_PIN,      // door lock
    REL_1_PIN,          
    REL_2_PIN,         
    REL_3_PIN,        
    REL_4_PIN,          
    REL_5_PIN,         
    REL_6_PIN,  
    REL_7_PIN          
};

enum REL_INIT {
    REL_DOOR_INIT = 1,                    // DESCRIPTION OF THE RELAY WIRING
    REL_1_INIT = 1,                    // DESCRIPTION OF THE RELAY WIRING
    REL_2_INIT = 1,                    // DESCRIPTION OF THE RELAY WIRING
    REL_3_INIT = 1,                    // DESCRIPTION OF THE RELAY WIRING
    REL_4_INIT = 1,                    // DESCRIPTION OF THE RELAY WIRING
    REL_5_INIT = 1,                    // DESCRIPTION OF THE RELAY WIRING
    REL_6_INIT = 1,                    // DESCRIPTION OF THE RELAY WIRING
    REL_7_INIT = 1                     // DESCRIPTION OF THE RELAY WIRING
};

const int relayPinArray[REL_AMOUNT] = {REL_DOOR_PIN};
const int relayInitArray[REL_AMOUNT] = {REL_DOOR_INIT};
