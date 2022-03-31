/*==========================================================================================================*/
/*		2CP - TeamEscape - Engineering
*		by Martin Pek
*
*
*/
/*==========================================================================================================*/

// I2C Port Expander
#include "header_s.h"
#include <PCF8574.h>
#include <stb_common.h>
#include <Wire.h>
// Watchdog timer
#include <avr/wdt.h>

#include <FastLED.h>


// == PN532 imports and setup
#include <stb_rfid.h>
#include <Adafruit_PN532.h>

// very manual but ... its C its gonna be bitching when it doesnt know during compilte time
// uncomment as needed
// for software SPI use (PN532_SCK, PN532_MISO, PN532_MOSI, RFID_SSPins[0])
Adafruit_PN532 RFID_0(RFID_SSPins[0]);

Adafruit_PN532 RFID_READERS[1] = {RFID_0}; //


CRGB LED_STRIPE_1[NR_OF_LEDS];

static CRGB LED_STRIPES[STRIPE_CNT] = {LED_STRIPE_1};

static bool game_live = false;
int rfid_ticks = 0;
// uint8_t last_read_uid[] = {0, 0, 0, 0, 0, 0, 0 };

/*==PCF8574=================================================================================================*/
Expander_PCF8574 relay;

void setup() {

    STB::begin();

    Serial.println("WDT endabled");
    //wdt_enable(WDTO_8S);
    wdt_reset();

    Serial.println();
    Serial.println("I2C: ... ");
    if (STB::i2cScanner()) {Serial.println("I2C: OK!");} else {Serial.println("I2C: FAILED!");}

    wdt_reset();

    STB::relayInit(relay, relayPinArray, relayInitArray, REL_AMOUNT);
    
    wdt_reset();

    Serial.println();
    Serial.println("LED: ... ");
    if (LED_init()) {Serial.println("LED: OK!");} else {Serial.println("LED: FAILED!");}

    wdt_reset();

    Serial.println();
    Serial.println("RFID: ... ");
    if (STB_RFID::RFIDInit(RFID_0)) {Serial.println("RFID: OK!");} else {Serial.println("RFID: FAILED!");}

    wdt_reset();

    Serial.println();
    STB::printSetupEnd();
}

void loop() {
    wdt_reset();
    /*
    led_set_all_clrs(CRGB::DarkRed, NR_OF_LEDS);
    LEDS.setBrightness(22); FastLED.show();
    delay(2000);
    LEDS.setBrightness(25); FastLED.show();
    delay(2000);
    LEDS.setBrightness(30); FastLED.show();
    delay(2000);
    wdt_reset();
    LEDS.setBrightness(33); FastLED.show();
    delay(2000);
    wdt_reset();
    LEDS.setBrightness(40); FastLED.show();
    delay(2000);
    wdt_reset();
    */


    if (game_live) {
        rfid_ticks = 0;
        while (!RFIDGatelocked()) {
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
        if (!RFIDGatelocked()) {
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
    LEDS.setBrightness(50); FastLED.show();
    led_set_all_clrs(CRGB::DarkRed, NR_OF_LEDS);
}

void end_game() {
    Serial.println("Game ended, have some light and an open door");
    LEDS.setBrightness(255);
    led_set_all_clrs(CRGB::Green, NR_OF_LEDS);
    wdt_reset();
    game_live = false;
    relay.digitalWrite(REL_DOOR_PIN, REL_DOOR_INIT);
};

bool LED_init() {

    // yep, exactly what it looks like...
    // we need to do it manually since we cannot define arrays easily for the preprocessor
    LEDS.addLeds<LED_STRIP_TYPE, RFID_1_LED_PIN, COLOR_ORDER>(LED_STRIPE_1, NR_OF_LEDS);
    delay(100);
    //LEDS.addLeds<LED_STRIP_TYPE, RFID_2_LED_PIN, COLOR_ORDER>(LED_STRIPE_2, NR_OF_LEDS);
    LEDS.setBrightness(255);
    delay(100);

    for (int stripe_nr = 0; stripe_nr < STRIPE_CNT; stripe_nr++) {
#ifdef DEBUGMODE
        led_set_clrs(stripe_nr, CRGB::Black, NR_OF_LEDS);
        Serial.print("LED stripe: "); Serial.println(stripe_nr);


        Serial.println("RED");
        led_set_clrs(stripe_nr, CRGB::Red, NR_OF_LEDS);
        delay(5000);
        wdt_reset();
        led_set_clrs(stripe_nr, CRGB::Green, NR_OF_LEDS);
        Serial.println("GREEN");
        delay(5000);
        wdt_reset();

        led_set_clrs(stripe_nr, CRGB::Black, NR_OF_LEDS);
        Serial.println("Green");
        wdt_reset();
#endif
    }
    led_set_all_clrs(CRGB::Green, NR_OF_LEDS);

    return true;
}

void led_set_all_clrs(CRGB clr, int led_cnt) {
    for(int stripe_nr=0; stripe_nr<STRIPE_CNT; stripe_nr++) {
        led_set_clrs(stripe_nr, clr, NR_OF_LEDS);
    }
}

void led_set_clrs(int stripe_nr, CRGB clr, int led_cnt) {
    delay(200);
    for(int i = 0; i < led_cnt; i++) {
        switch(stripe_nr) {
            case 0:
                LED_STRIPE_1[i] = clr; break;
            default: Serial.println("wrong led selection"); break;
        }
    }
    FastLED.show();
    delay(10*led_cnt);
}


bool RFIDGatelocked() {

    uint8_t data[16];

    /*
    int cards_present[RFID_AMOUNT];
    memset(cards_present, 0, sizeof(cards_present));
    int cards_present_cnt = 0;
    */

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

void dbg_println(String print_dbg) {
#ifdef DEBUGMODE
    Serial.println(print_dbg);
#endif
}
