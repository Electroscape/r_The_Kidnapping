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


// for software SPI use (PN532_SCK, PN532_MISO, PN532_MOSI, RFID_SSPins[0])
Adafruit_PN532 RFID_0(RFID_SSPins[0]);
Adafruit_PN532 RFID_READERS[1] = {RFID_0};
uint8_t data[16];
unsigned long lastRfidCheck = millis();

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
    Serial.println("RFID start");
    Serial.flush();

    lastRfidCheck = millis();
    char message[32] = "!RFID";

    for (int readerNo = 0; readerNo < RFID_AMOUNT; readerNo++) {
        if (STB_RFID::cardRead(RFID_READERS[0], data, RFID_DATABLOCK)) {
            strcat(message, "_");
            strcat(message, (char*) data);
        }
    }

    Serial.println("RFID message adding");
    Serial.flush();

    STB.defaultOled.clear();
    STB.defaultOled.println(message);
    STB.rs485AddToBuffer(message);

    Serial.println("RFID end");
    Serial.flush();
}

