/**
 * @file BREAKOUT.ino
 * @author Martin Pek (martin.pek@web.de)
 * @brief 
 * @version 0.1
 * @date 2022-04-01
 * 
 * 
 */

#include "header_s.h"
// I2C Port Expander
#include <PCF8574.h>
#include <stb_common.h>
#include <Wire.h>
// Watchdog timer
#include <avr/wdt.h>

// == PN532 imports and setup
#include <stb_rfid.h>
#include <Adafruit_PN532.h>

#include <Adafruit_NeoPixel.h>
#include <stb_led.h>

Adafruit_NeoPixel LED_Strips[STRIPE_CNT];
const long int darked = LED_Strips[0].Color(120,0,0);
const long int green = LED_Strips[0].Color(0,255,0);


// for software SPI use (PN532_SCK, PN532_MISO, PN532_MOSI, RFID_SSPins[0])
Adafruit_PN532 RFID_0(RFID_SSPins[0]);
Adafruit_PN532 RFID_READERS[1] = {RFID_0};

static bool game_live = false;
int rfid_ticks = 0;

Expander_PCF8574 relay;

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


    wdt_reset();

    Serial.println();
    Serial.println("RFID: ... ");
    if (STB_RFID::RFIDInit(RFID_0)) {Serial.println("RFID: OK!");} else {Serial.println("RFID: FAILED!");}

    wdt_reset();

    //  Caution! there is a conflict with the PN532 library
    // having the led_init before the reader will cause it to fail
    Serial.println();
    Serial.println("LED: ... ");
    if (STB_LED::ledInit(LED_Strips, ledCnts, ledPins, NEO_BRG)) {Serial.println("LED: OK!");} else {Serial.println("LED: FAILED!");}
    STB_LED::setAllStripsToClr(LED_Strips, darked);

    Serial.println();
    STB::printSetupEnd();
}

void loop() {
    wdt_reset();

    if (game_live) {
        rfid_ticks = 0;
        while (!rfidGateLocked()) {
            rfid_ticks++;
            if (rfid_ticks > RFID_TICKS_REQUIRED) {
                end_game();
                break;
            }
            delay(50);
        }
    } else {
        wait_for_reset();
    }

    Serial.println("Loop");
    delay(500);
}

void wait_for_reset() {

    wdt_reset();
    uint8_t reset_timer = 0;
    Serial.println("room is not live, waiting for card being removed to arm the room");


    while (reset_timer < RESET_DURATION) {
        wdt_reset();
        if (!rfidGateLocked()) {
            Serial.println("card present, resettimer set to 0");
            reset_timer = 0;
        } else {
            Serial.println("card removed, increasing timer");
            reset_timer += 5;
        }
        delay(5000);
        wdt_reset();
    }
    Serial.println("Game going live, killing lights and locking the door");
    game_live = true;
    relay.digitalWrite(REL_DOOR_PIN, !REL_DOOR_INIT);
    STB_LED::setAllStripsToClr(LED_Strips, darked);
}

void end_game() {
    Serial.println("Game ended, have some light and an open door");
    STB_LED::setAllStripsToClr(LED_Strips, green);
    wdt_reset();
    game_live = false;
    relay.digitalWrite(REL_DOOR_PIN, REL_DOOR_INIT);
};


bool rfidGateLocked() {

    uint8_t data[16];

    for (int reader_nr=0; reader_nr<RFID_AMOUNT; reader_nr++) {

        Serial.print("Checking presence for reader: ");Serial.println(reader_nr);

        if (STB_RFID::cardRead(RFID_READERS[reader_nr], data, RFID_DATABLOCK)) {

            Serial.println((char *) data);
            if (strcmp(RFID_solutions[0], (char *) data)) {
                Serial.println("Correct card placed!");
                relay.digitalWrite(REL_DOOR_PIN, REL_DOOR_INIT);
                return false;
            }
        } else  {
            relay.digitalWrite(REL_DOOR_PIN, !REL_DOOR_INIT);
            delay(50);
        }
        
    }

    Serial.print("\n");
    return true;
}

