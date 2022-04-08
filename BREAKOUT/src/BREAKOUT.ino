/**
 * @file BREAKOUT.ino
 * @author Martin Pek (martin.pek@web.de)
 * @brief 
 * @version 0.1
 * @date 6.04.2022
 * 
 */

String versionDate = "6.04.2022";
String version = "1.4.2";

#include "header_st.h"
// I2C Port Expander

#include <stb_common.h>
#include <avr/wdt.h>

#include <stb_rfid.h>
#include <stb_led.h>
#include <stb_oled.h>

// #define ledDisable 0
// #define rfidDisable 1
// #define oledDisable 1

SSD1306AsciiWire oled;

Adafruit_NeoPixel LED_Strips[STRIPE_CNT];
const long int darked = LED_Strips[0].Color(120,0,0);
const long int green = LED_Strips[0].Color(0,255,0);


// for software SPI use (PN532_SCK, PN532_MISO, PN532_MOSI, RFID_SSPins[0])
Adafruit_PN532 RFID_0(RFID_SSPins[0]);
Adafruit_PN532 RFID_READERS[1] = {RFID_0};

bool gameLive = true;
int rfidTicks = 0;      // ticks of the correct RFID placed
int resetTimer = 0;     // ticks to trigger the game going live again

PCF8574 relay;

void setup() {

    STB::begin();

    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);
    wdt_reset();

    Serial.println();
    Serial.println("I2C: ... ");
    if (STB::i2cScanner()) {Serial.println("I2C: OK!");} else {Serial.println("I2C: FAILED!");}

    wdt_reset();

    STB::relayInit(relay, relayPinArray, relayInitArray, REL_AMOUNT);

    
    wdt_reset();

    Serial.println();
    Serial.println("RFID: ... ");

#ifndef rfidDisable
    if (STB_RFID::RFIDInit(RFID_0)) {Serial.println("RFID: OK!");} else {Serial.println("RFID: FAILED!");}
    wdt_reset();
#endif

#ifndef oledDisable
    // STB_OLED::oledInit(&oled, SH1106_128x64);
    oled.begin(&SH1106_128x64, OLED_I2C_ADD);
    oled.set400kHz();
    oled.setScroll(true);
    oled.setFont(Verdana12_bold);
    oled.clear();
    oled.println("  System startup...");  
#endif  

#ifndef ledDisable
    Serial.println();
    Serial.println("LED: ... ");
    if (STB_LED::ledInit(LED_Strips, ledCnts, ledPins, NEO_BRG)) {Serial.println("LED: OK!");} else {Serial.println("LED: FAILED!");}
#endif

    Serial.println();
    STB::printSetupEnd();

    initGame();
}

void loop() {
    // Serial.println("loop");
#ifndef rfidDisable
    if (gameLive) {
        runGame();
    } else {
        waitForReset();
    }
#endif
    wdt_reset();
}

void runGame() {
    if (rfidCorrect()) {
        if (rfidTicks > RFID_TICKS_REQUIRED) {
            endGame();
        }
        rfidTicks++;
        
    } else {
        rfidTicks = 0;
    }
    delay(50);
}

void waitForReset() {

    Serial.println("room has been solved, waiting for card being removed to arm the room");

    if (rfidCorrect()) {
        Serial.println("card still present");
        resetTimer = 0;
    } else {
        Serial.println("card removed, increasing timer");
        resetTimer += 5;
    }

    if (resetTimer > RESET_DURATION) {
        initGame();
    } else {
        delay(5000);
    }

}

void endGame() {
#ifndef oledDisable
    oled.clear();
    oled.println("Game ended\n green lights\n open door");
#endif
    Serial.println("Game ended, have some light and an open door");
    gameLive = false;
    relay.digitalWrite(REL_DOOR_PIN, REL_DOOR_INIT);
#ifndef ledDisable
    STB_LED::setAllStripsToClr(LED_Strips, green);
#endif
};

void initGame() {
    resetTimer = 0;
    Serial.println("Game going live, killing lights and locking the door");
#ifndef oledDisable
    oled.clear();
    oled.println("Game live\n killing lights\n locking");
#endif
    gameLive = true;
    relay.digitalWrite(REL_DOOR_PIN, !REL_DOOR_INIT);
#ifndef ledDisable
    STB_LED::setAllStripsToClr(LED_Strips, darked);
#endif
}


bool rfidCorrect() {

    uint8_t data[16];
    Serial.println("Checking presence for reader");

    if (STB_RFID::cardRead(RFID_READERS[0], data, RFID_DATABLOCK)) {

        Serial.println((char *) data);
        if (strcmp(RFID_solutions[0], (char *) data)) {
            Serial.println("Correct card placed!");
            return true;
        }
    }
        
    return false;
}

