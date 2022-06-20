/**
*   2CP - TeamEscape - Engineering
*   Author Martin Pek
*
*/

/**************************************************************************/
// Setting Configurations
#include "header_st.h"

#include <stb_common.h>
#include <avr/wdt.h>


STB STB;

// PCF8574 relay;
PCF8574 reset;
int lineCnt = 0;

void startGame() {
    // Led stuff
    STB.motherRelay.digitalWrite(REL_0_PIN, REL_0_INIT);
}

void endGame() {
    Serial.println("ENDGAME!!");
    // Led stuff
    STB.motherRelay.digitalWrite(REL_0_PIN, !REL_0_INIT);
}

void setup() {
    STB.begin();
    STB.rs485SetToMaster();
    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);

    STB.i2cScanner();
    reset.begin(0x3D);
    for (int i = 0; i < 8; i++) {
        reset.pinMode(i, OUTPUT);
    }
    
    wdt_reset();
    STB.printSetupEnd();
    STB.dbgln("MOther");
}

/*======================================
//===LOOP==============================
//====================================*/
void loop() {
    STB.rs485PerformPoll();
    while (STB.rs485RcvdNextLn() && lineCnt++ < 5) {
        
        Serial.println("motherloop");
        char* ptr = strtok(STB.rcvdPtr, "_");
        ptr = strtok(NULL, "_");
        if (ptr != NULL) {
            Serial.println(ptr);
            delay(1000);
            if (strncmp(rfidSolutions[0], ptr, 2) == 0) {
                endGame();
            } else if (strncmp(rfidSolutions[0], ptr, 3) == 0) {
                // do a reset here
            }
        }
    }
    lineCnt = 0;
    wdt_reset();
}
