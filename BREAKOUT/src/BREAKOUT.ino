/**
 * @file BREAKOUT.ino
 * @author Martin Pek (martin.pek@web.de)
 * @brief 
 * @version 1.6.2
 * @date 30.06.2022
 * build with lib_arduino v0.6.2
 */

/*
test Todo:
removed oled
remove wdt
use interruptcheck
switch SPI port

test completed:
delays
setup order
basic code RFID
removed Leds

works with a blank example 
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

#ifndef ledDisable
#define FASTLED_INTERRUPT_RETRY_COUNT 1
Adafruit_NeoPixel LED_Strips[STRIPE_CNT];
const long int green = LED_Strips[0].Color(0,255,0);
#endif
char ledKeyword[] = "!LED";



// for software SPI use (PN532_SCK, PN532_MISO, PN532_MOSI, RFID_SSPins[0])
#ifndef rfidDisable
    Adafruit_PN532 RFID_0(RFID_SSPins[0]);
    Adafruit_PN532 RFID_READERS[1] = {RFID_0};
    uint8_t data[16];
    unsigned long lastRfidCheck = millis();
#endif


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
    STB_LED::ledInit(LED_Strips, 1, ledCnts, ledPins, NEO_BRG);
#endif

    wdt_reset();

    STB.printSetupEnd();
}


void loop() {

    // if (Serial.available()) { Serial.write(Serial.read()); }

    #ifndef rfidDisable
        rfidRead();
    #endif

    STB.rs485SlaveRespond();

    while (STB.rcvdPtr != NULL) {
        
        if (strncmp((char *) ledKeyword, STB.rcvdPtr, 4) == 0) {
            
            char *cmdPtr = strtok(STB.rcvdPtr, "_");
            cmdPtr = strtok(NULL, "_");

            int i = 0;
            int values[3] = {0,0,0};

            while (cmdPtr != NULL && i < 3) {
                // STB.dbgln(cmdPtr);
                sscanf(cmdPtr,"%d", &values[i]);
                //STB.dbgln(String(values[i]));
                cmdPtr = strtok(NULL, "_");
                i++;
            }

          
            if (i == 3) {
                // STB.dbgln("I == 2");
                #ifndef ledDisable
                // double check this since the led stripes for testing may not be identical
                long int setClr = LED_Strips[0].Color(values[0],values[2],values[1]);
                STB_LED::setAllStripsToClr(LED_Strips, 1, setClr);
                STB.rs485SendAck();
                #endif
            }
            
        }
       
        STB.rs485RcvdNextLn();
    }

    wdt_reset();
}

#ifndef rfidDisable
void rfidRead() {
    if (millis() - lastRfidCheck < rfidCheckInterval) {
        return;
    }

    lastRfidCheck = millis();
    char message[32] = "!RFID";

    Serial.println("RFID start");
    Serial.flush();

    for (int readerNo = 0; readerNo < RFID_AMOUNT; readerNo++) {
        if (STB_RFID::cardRead(RFID_READERS[0], data, RFID_DATABLOCK)) {
            Serial.println("RFID read succees");
            Serial.flush();
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
#endif

void interruptCheck() {
    unsigned long startTime = millis();
    delay(10);
    Serial.print("interruptcheck attempt ...");
    Serial.flush();
    while (millis() - startTime < 9 ) {}
    Serial.println("success");
    Serial.flush();
    delay(10);
}
