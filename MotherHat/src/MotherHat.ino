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
    while (STB.rs485RcvdNextLn() && lineCnt < 5) {
        STB.dbgln(String(lineCnt));
        STB.dbgln("nextline: ");
        STB.dbgln(String(STB.rcvdLn));
        lineCnt++;
        wdt_reset();
        delay(2000);
    }
    wdt_reset();
}
