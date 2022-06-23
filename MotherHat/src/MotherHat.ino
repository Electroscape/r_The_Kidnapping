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
PCF8574 resetPCF;
int lineCnt = 0;
unsigned long presentationTimestamp = millis();
int currentCardType = -1;

void startGame() {
    Serial.println("STARTGAME!!");
    STB.motherRelay.digitalWrite(REL_0_PIN, REL_0_INIT);
    // const long int darked = LED_Strips[0].Color(120,0,0);
    STB.rs485AddToBuffer("!Poll0\n!LED_120_0_0");
    STB.rs485SendBuffer();
}

void endGame() {
    Serial.println("ENDGAME!!");
    STB.motherRelay.digitalWrite(REL_0_PIN, !REL_0_INIT);
    // // const long int green = LED_Strips[0].Color(0,255,0);
    STB.rs485AddToBuffer("!Poll0\n!LED_0_255_0");
    STB.rs485SendBuffer();
}

void setup() {
    STB.begin();
    STB.rs485SetToMaster();
    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);

    STB.i2cScanner();
    resetPCF.begin(0x3D);
    for (int i = 0; i < 8; i++) {
        resetPCF.pinMode(i, OUTPUT);
        resetPCF.digitalWrite(i,1);
    }
    
    wdt_reset();
    STB.printSetupEnd();
    STB.dbgln("MOther");

    startGame();
}

/*======================================
//===LOOP==============================
//====================================*/
void loop() {
    STB.rs485PerformPoll();
    while (STB.rs485RcvdNextLn() && lineCnt++ < 5) {

        char* ptr = strtok(STB.rcvdPtr, "_");
        if (strcmp("!RFID", ptr) != 0) {
            continue; // skip all the other checks since its not RFID cmd
        }
        ptr = strtok(NULL, "_");
        if (ptr != NULL) {
            Serial.print("card is: "); Serial.println(ptr);
            // cannot use a dynamic variable with strcmp since it needs const char* with for loop here ... 
            if (strncmp(rfidSolutions[unlock], ptr, 2) == 0) {
                if (currentCardType != unlock) {
                    presentationTimestamp = millis();
                    currentCardType = unlock;
                }
            } else if (strncmp(rfidSolutions[reset], ptr, 3) == 0) {
                if (currentCardType != reset) {
                    presentationTimestamp = millis();
                    currentCardType = reset;
                }
            } else {
                currentCardType = -1;
            }

        } else {
            currentCardType = -1; // i dont like doing this twice ...
        }

        if (currentCardType >= 0 && millis() - presentationTimestamp > presentationTime[currentCardType]) {
            switch (currentCardType) {
                case cardType::unlock: endGame(); break;
                case cardType::reset: startGame(); break;
            }
        }

    }

    lineCnt = 0;
    wdt_reset();
}
