#pragma once

String title = "Stuttgart Gallery A/B";
String versionDate = "02.02.2021";
String version = "version 1.0ST";
String brainName = String("BrRFID");
String relayCode = String("UVL");

#define LIGHT_ON 0
#define LIGHT_OFF 1
#define MAX485_WRITE HIGH
#define MAX485_READ LOW
#define OLED_DISABLE true

// I2C Addresses
#define LCD_I2C_ADD 0x27    // Predefined by hardware
#define OLED_ADD 0x3C   // Predefined by hardware
#define RELAY_I2C_ADD 0x3F  // Relay Expander

#define CLR_ORDER NEO_RGB

// --- LED settings --- 
#define NR_OF_LEDS             1  /* Anzahl der Pixel auf einem Strang (Test 1 Pixel)                   */
#define STRIPE_CNT             3

#define RFID_1_LED_PIN          9     /* Per Konvention ist dies RFID-Port 1                                */
#define RFID_2_LED_PIN          6     /* Per Konvention ist dies RFID-Port 2                                */
#define RFID_3_LED_PIN          5     /* Per Konvention ist dies RFID-Port 3                                */
#define RFID_4_LED_PIN          3     /* Per Konvention ist dies RFID-Port 4   */

int ledCnts[STRIPE_CNT] = {9};
int ledPins[STRIPE_CNT] = {RFID_1_LED_PIN, RFID_2_LED_PIN, RFID_3_LED_PIN};

enum cardType {unlock, reset};
char rfidSolutions[2][5] = {"AH\0", "RES\0"};

unsigned long  presentationTime[2] = {500 ,3000};

// RFIDs
#define RFID_AMOUNT 8

// == constants
// RELAY
enum REL_PIN {
    REL_0_PIN,        // 0 Exit door
    REL_1_PIN,  
    REL_2_PIN,  
    REL_3_PIN,        
    REL_4_PIN,        
    REL_5_PIN,        
    REL_6_PIN,       
    REL_7_PIN        
};
enum REL_INIT {                 // DESCRIPTION OF THE RELAY WIRING
    REL_0_INIT = 1,                
    REL_1_INIT = 1,                 
    REL_2_INIT = 1,  
    REL_3_INIT = 1,                
    REL_4_INIT = 1,                
    REL_5_INIT = 1,              
    REL_6_INIT = 1,              // NC = Empty | COM = 24V  | NO = Valve
    REL_7_INIT = 1                
};

#define REL_AMOUNT 8

int relayPinArray[REL_AMOUNT] = {
    REL_0_PIN,
    REL_1_PIN,
    REL_2_PIN,
    REL_3_PIN,
    REL_4_PIN,
    REL_5_PIN,
    REL_6_PIN,
    REL_7_PIN
};
int relayInitArray[REL_AMOUNT] = {
    REL_0_INIT,
    REL_1_INIT,
    REL_2_INIT,
    REL_3_INIT,
    REL_4_INIT,
    REL_5_INIT,
    REL_6_INIT,
    REL_7_INIT
};
