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
#include <stb_namespace.h>
using namespace stb_namespace;
#include <Wire.h>
//Watchdog timer
#include <avr/wdt.h>

#include <FastLED.h>


// == PN532 imports and setup

#include <Adafruit_PN532.h>


// very manual but ... its C its gonna be bitching when it doesnt know during compilte time
// uncomment as needed
const Adafruit_PN532 RFID_0(PN532_SCK, PN532_MISO, PN532_MOSI, RFID_SSPins[0]);

const Adafruit_PN532 RFID_READERS[1] = {RFID_0}; //


CRGB LED_STRIPE_1[NR_OF_LEDS];
//CRGB LED_STRIPE_2[NR_OF_LEDS];

static CRGB LED_STRIPES[STRIPE_CNT] = {LED_STRIPE_1};

static bool game_live = false;
int rfid_ticks = 0;
// uint8_t last_read_uid[] = {0, 0, 0, 0, 0, 0, 0 };

/*==PCF8574=================================================================================================*/
Expander_PCF8574 relay;

void setup() {

    communication_init();
    Serial.println("WDT endabled");
    //wdt_enable(WDTO_8S);
    wdt_reset();

    Serial.println();
    Serial.println("I2C: ... ");
    if (i2c_scanner()) {Serial.println("I2C: OK!");} else {Serial.println("I2C: FAILED!");}

    wdt_reset();

    printWithHeader("!header_begin", "SYS");
    stb_namespace::relay_init(relay, *relayPinArray, *relayInitArray);

    wdt_reset();

    Serial.println();
    Serial.println("LED: ... ");
    if (LED_init()) {Serial.println("LED: OK!");} else {Serial.println("LED: FAILED!");}

    wdt_reset();

    Serial.println();
    Serial.println("RFID: ... ");
    if (RFID_Init()) {Serial.println("RFID: OK!");} else {Serial.println("RFID: FAILED!");}

    wdt_reset();

    Serial.println();
    print_setup_end();
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
        while (!RFID_Gate_locked()) {
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
        if (!RFID_Gate_locked()) {
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

// RFID functions

bool RFID_Init() {

    for (int i=0; i<RFID_AMOUNT; i++) {

        delay(20);
        wdt_reset();

        Serial.print("initializing reader: "); Serial.println(i);
        RFID_READERS[i].begin();
        RFID_READERS[i].setPassiveActivationRetries(5);

        int retries = 0;
        while (true) {
            uint32_t versiondata = RFID_READERS[i].getFirmwareVersion();
            if (!versiondata) {
                Serial.println("Didn't find PN53x board");
                if (retries > 5) {
                    Serial.println("PN532 startup timed out, restarting");
                    software_Reset();
                }
            } else {
                Serial.print("Found chip PN5"); Serial.println((versiondata>>24) & 0xFF, HEX);
                Serial.print("Firmware ver. "); Serial.print((versiondata>>16) & 0xFF, DEC);
                Serial.print('.'); Serial.println((versiondata>>8) & 0xFF, DEC);
                break;
            }
            retries++;
        }
        // configure board to read RFID tags
        RFID_READERS[i].SAMConfig();
        delay(20);
        wdt_reset();
    }
    return true;
}

bool RFID_Gate_locked() {

    uint8_t success;
    uint8_t uid[] = {0, 0, 0, 0, 0, 0, 0 };  // Buffer to store the returned UID
    uint8_t uidLength;
    uint8_t data[16];
    bool gate_locked = false;

    int cards_present[RFID_AMOUNT];
    memset(cards_present, 0, sizeof(cards_present));
    int cards_present_cnt = 0;

    for (int reader_nr=0; reader_nr<RFID_AMOUNT; reader_nr++) {

        Serial.print("Checking presence for reader: ");Serial.println(reader_nr);

        success = RFID_READERS[reader_nr].readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);
        // memccpy(last_read_uid, uid, sizeof(uid));
        if (success) {
            Serial.println("Card present on reader!");
#ifdef DEBUGMODE
            // PN532DEBUGPRINT needs to be enabled
            // RFID_READERS[reader_nr].PrintHex(uid, uidLength);
#endif
            cards_present[reader_nr] = 1;
            cards_present_cnt++;

            if (uidLength != 4) {
                Serial.println("Card is not Mifare classic, discarding card");
                gate_locked = true;
                continue;
            }

            if (!read_PN532(reader_nr, data, uid, uidLength)) {
                Serial.println("read failed");
                gate_locked = true;
                continue;
            }
#ifdef DEBUGMODE
            // PN532DEBUGPRINT needs to be enabled
            // RFID_READERS[reader_nr].PrintHexChar(data, 16);
#endif
            if (!data_correct(reader_nr, data)) {
                gate_locked = true;
                continue;
            }

        } else {
            dbg_println("No presence on the reader!");
            cards_present[reader_nr] = 0;
            gate_locked = true;
        }
        delay(50);
    }

    // adjusting of colours needs to be delayed otherwise we may get interfence
    delay(20);

    Serial.print("\n");
    return gate_locked;
}

bool read_PN532(int reader_nr, uint8_t *data, uint8_t *uid, uint8_t uidLength) {

    uint8_t success;
    wdt_reset();
    // authentication may be shifted to another function if we need to expand
    success = RFID_READERS[reader_nr].mifareclassic_AuthenticateBlock(uid, uidLength, RFID_DATABLOCK, 0, keya);
    dbg_println("Trying to authenticate block 4 with default KEYA value");
    if (!success) {
        dbg_println("Authentication failed, card may already be authenticated");
    }

    success = RFID_READERS[reader_nr].mifareclassic_ReadDataBlock(RFID_DATABLOCK, data);
    if (!success) {
        Serial.println("Reading failed, discarding card");
        return false;
    }
    return true;
}

bool data_correct(int current_reader, uint8_t *data) {
    uint8_t result = -1;

    for (int solution=0; solution<RFID_AMOUNT; solution++) {

        for (int i=0; i<RFID_SOLUTION_SIZE; i++) {
            if (RFID_solutions[solution][i] != data[i]) {
                // We still check for the other solutions to show the color
                // but we display it being the wrong solution of the riddle
                if (solution == current_reader) {
                    Serial.print("Wrong card placed on reader: "); Serial.println(current_reader);
                }
                continue;
            } else {
                if (i >= RFID_SOLUTION_SIZE - 1) {
                    // its a valid card but not placed on the right socket
                    Serial.print("equal to result of reader");
                    delay(5);
                    // dbg_println(solution);
                    result = solution;
                }
            }
        }

    }

    // handling of the colours of the individual cards
    if (result < 0) {
        Serial.print("undefined card placed on reader: "); Serial.println(current_reader);
    }

    if (result == current_reader) {
        Serial.print("Correct card placed on reader: "); Serial.println(current_reader);
        return true;
    } else {
        return false;
    }
}

void dbg_println(String print_dbg) {
#ifdef DEBUGMODE
    Serial.println(print_dbg);
#endif
}

void communication_init() {
    Wire.begin();
    Serial.begin(115200);
    delay(20);
    print_serial_header();
}

void print_serial_header() {
    print_logo_infos(title);

    Serial.println("!header_begin");
    Serial.println(title);
    Serial.println(versionDate);
    Serial.println(version);
}

void print_logo_infos(String progTitle) {
    Serial.println(F("+-----------------------------------+"));
    Serial.println(F("|    TeamEscape HH&S ENGINEERING    |"));
    Serial.println(F("+-----------------------------------+"));
    Serial.println();
    Serial.println(progTitle);
    Serial.println();
    delay(20);
}

void print_setup_end() {
    Serial.println("!setup_end");
    Serial.println(); Serial.println("===================START====================="); Serial.println();
}

bool i2c_scanner() {
    Serial.println (F("I2C scanner:"));
    Serial.println (F("Scanning..."));
    byte wire_device_count = 0;

    for (byte i = 8; i < 120; i++) {
        Wire.beginTransmission (i);
        if (Wire.endTransmission () == 0) {
            Serial.print   (F("Found address: "));
            Serial.print   (i, DEC);
            Serial.print   (F(" (0x"));
            Serial.print   (i, HEX);
            Serial.print (F(")"));
            if (i == 39) Serial.print(F(" -> LCD"));
            if (i == 56) Serial.print(F(" -> LCD-I2C-Board"));
            if (i == 57) Serial.print(F(" -> Input-I2C-board"));
            if (i == 60) Serial.print(F(" -> Display"));
            if (i == 63) Serial.print(F(" -> Relay"));
            if (i == 22) Serial.print(F(" -> Servo-I2C-Board"));
            Serial.println();
            wire_device_count++;
            delay (3);
        }
    }
    Serial.print   (F("Found "));
    Serial.print   (wire_device_count, DEC);
    Serial.println (F(" device(s)."));
    Serial.println("successfully scanned I2C");
    Serial.println();

    return true;
}

void software_Reset() {
    Serial.println(F("Restarting in"));
    delay(50);
    for (byte i = 3; i>0; i--) {
        Serial.println(i);
        delay(100);
    }
    asm volatile ("  jmp 0");
}
