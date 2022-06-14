/**
 * @file BREAKOUT.ino
 * @author Martin Pek (martin.pek@web.de)
 * @brief 
 * @version 0.1
 * @date 22.04.2022
 * 
 */

String versionDate = "6.04.2022";
String version = "1.5.0";

#include "header_st.h"
// I2C Port Expander

#include <stb_common.h>
#include <avr/wdt.h>

#include <stb_rfid.h>
#include <stb_led.h>
#include <stb_oled.h>

// #define ledDisable 1
// #define rfidDisable 1
// #define relayDisable 1

STB STB;

Adafruit_NeoPixel LED_Strips[STRIPE_CNT];
const long int darked = LED_Strips[0].Color(120,0,0);
const long int green = LED_Strips[0].Color(0,255,0);


// for software SPI use (PN532_SCK, PN532_MISO, PN532_MOSI, RFID_SSPins[0])
Adafruit_PN532 RFID_0(RFID_SSPins[0]);
Adafruit_PN532 RFID_READERS[1] = {RFID_0};
uint8_t data[16];
unsigned long lastRfidCheck = millis();

bool gameLive = true;
int rfidTicks = 0;      // ticks of the correct RFID placed
int resetTimer = 0;     // ticks to trigger the game going live again

PCF8574 relay;

void setup() {

    STB.begin();
    STB.rs485SetSlaveAddr(0);

    STB.dbgln("WDT endabled");
    wdt_enable(WDTO_8S);
    wdt_reset();

    STB.i2cScanner();
    wdt_reset();

#ifndef rfidDisable
    STB_RFID::RFIDInit(RFID_0);
    wdt_reset();
#endif

#ifndef ledDisable
    STB_LED::ledInit(LED_Strips, ledCnts, ledPins, NEO_BRG);
#endif

    wdt_reset();

    STB.printSetupEnd();
}

void loop() {
    rfidRead();
    STB.rs485SlaveRespond();
    wdt_reset();
}


void rfidRead() {
    if (millis() - lastRfidCheck < rfidCheckInterval) {
        return;
    }

    lastRfidCheck = millis();

    Serial.println("Checking presence for reader");
    if (STB_RFID::cardRead(RFID_READERS[0], data, RFID_DATABLOCK)) {
        
    }
}

