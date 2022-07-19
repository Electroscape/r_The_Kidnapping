/**
*   2CP - TeamEscape - Engineering
*   Author Martin Pek
*   @date 30.06.2022
*   build with lib_arduino v0.6.2
*/

/**************************************************************************/
// Setting Configurations
#include "header_st.h"

#include <stb_common.h>
#include <avr/wdt.h>
#include <stb_mother_ledCmds.h>


STB STB;

// PCF8574 relay;
// PCF8574 resetPCF;

int lineCnt = 0;
unsigned long presentationTimestamp = millis();
int currentCardType = -1;
bool solvedState = true;


void startGame() {

    // game already ready, no need to spam LED cmds 
    if (!solvedState) {return;}

    Serial.println("STARTGAME!!");
    STB.motherRelay.digitalWrite(REL_0_PIN, REL_0_INIT);
    LED_CMDS::setToClr(STB, 1, LED_CMDS::clrRed, 50);

    solvedState = false;

}


void endGame() {

    // game already solved, no need to spam LED cmds 
    if (solvedState) {return;}

    Serial.println("ENDGAME!!");
    STB.motherRelay.digitalWrite(REL_0_PIN, !REL_0_INIT);
    LED_CMDS::setToClr(STB, 1, LED_CMDS::clrGreen, 50);

    solvedState = true;
}


void setup() {
    STB.begin();

    STB.i2cScanner();

    STB.rs485SetToMaster();
    STB.rs485SetSlaveCount(1);

    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);


    /*
    resetPCF.begin(0x3D);
    for (int i = 0; i < 8; i++) {
        resetPCF.pinMode(i, OUTPUT);
        resetPCF.digitalWrite(i,1);
    }
    */
    
    wdt_reset();
    STB.printSetupEnd();

    startGame();
}


void loop() {
    
    STB.rs485PerformPoll();

    while (STB.rs485RcvdNextLn() && lineCnt++ < 5) {

        char* ptr = strtok(STB.rcvdPtr, "_");
        if (strcmp("!RFID", ptr) != 0) {
            continue; // skip all the other checks since its not RFID cmd
        }
        ptr = strtok(NULL, "_");
        if (ptr != NULL) {
            STB.dbgln("card detected: "); 
            STB.dbgln(ptr);
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
