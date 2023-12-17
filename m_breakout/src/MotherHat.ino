/**
*   2CP - TeamEscape - Engineering
*   Author Martin Pek
*   @date 30.06.2022
*   build with lib_arduino v0.6.2
*/

/**************************************************************************/


#include <stb_mother.h>
#include <stb_mother_IO.h>
// #include <stb_keypadCmds.h>
// #include <stb_oledCmds.h>
#include <stb_mother_ledCmds.h>

// Setting Configurations
#include "header_st.h"

PCF8574 inputPCF;
STB_MOTHER Mother;
STB_MOTHER_IO MotherIO;

int stage = stages::off;
int stageIndex = 0;
int lastStage = -1;
int lastResult = 0;

// int inputTicks = 0;

int validBrainResult = 0;


bool passwordInterpreter(char* password) {
    // Mother.STB_.defaultOled.clear();
    Serial.print("Handling pw");
    Serial.println(password);
    for (int passNo=0; passNo < PasswordAmount; passNo++) {
        if (passwordMap[passNo] & stage) {
            if ( strncmp(passwords[passNo], password, strlen(passwords[passNo]) ) == 0) {
                Serial.println("Correct PW");
                return true;
            }
        }
    }
    return false;
}


void handleResult() {
    Mother.STB_.rcvdPtr = strtok(Mother.STB_.rcvdPtr, KeywordsList::delimiter.c_str());
    if ((Mother.STB_.rcvdPtr != NULL) && passwordInterpreter(Mother.STB_.rcvdPtr)) {
        stage = stages::solved;
    }
}


// again good candidate for a mother specific lib
bool checkForRfid() {
    if (strncmp(KeywordsList::rfidKeyword.c_str(), Mother.STB_.rcvdPtr, KeywordsList::rfidKeyword.length() ) != 0) {
        return false;
    } 
    Mother.STB_.rcvdPtr += KeywordsList::rfidKeyword.length();

    if (stage > stages::off) {
        handleResult();
        return true;
    }
    return false;
}


void interpreter() {
    while (Mother.nextRcvdLn()) {
        checkForRfid();
    }
}


void stageActions() {
    wdt_reset();
    switch (stage) {
        case solved:
            Mother.motherRelay.digitalWrite(relays::door, doorOpen);
            LED_CMDS::setStripToClr(Mother, ledBrain, LED_CMDS::clrGreen, 50, 0);
            MotherIO.setOuput(outSolved);
            delay(200);
            MotherIO.outputReset();
        break;
        case idle:
            LED_CMDS::setStripToClr(Mother, ledBrain, LED_CMDS::clrRed, 50, 0);
        break;
    }
}


void stageUpdate() {
    if (lastStage == stage) { return; }
    Serial.print("Stage is:");
    Serial.println(stage);
        
    if (stageIndex < 0) {
        Serial.println(F("Stages out of index!"));
        delay(15000);    
    }

    // important to do this before stageActions! otherwise we skip stages
    lastStage = stage;

    // for now no need to make it work properly scaling, need to build afnc repertoir anyways
    MotherIO.outputReset();
    stageActions();
}


void handleInputs() {
    int result = MotherIO.getInputs();
    if (result == lastResult) { return; }
    lastResult = result;

    switch (result) {
        case inputValues::roomReset:
            stage = idle;
        break;
        case inputValues::setSolved:
            stage = solved;
        break;
    }
}



void setup() {
    Mother.begin();
    Mother.relayInit(relayPinArray, relayInitArray, relayAmount);
    MotherIO.ioInit(intputArray, sizeof(intputArray), outputArray, sizeof(outputArray));

    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);

    // technically 3 but for the first segments till unlocked there is no need
    Mother.rs485SetSlaveCount(1);

    wdt_reset();
    delay(1000);
}


void loop() {
    validBrainResult = Mother.rs485PerformPoll(2);
    if (validBrainResult) {interpreter();}
    handleInputs();    
    stageUpdate(); 
    delay(50);
    wdt_reset();
}
