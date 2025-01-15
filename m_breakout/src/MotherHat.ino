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
    Serial.print("Handling pw ");
    Serial.println(password);

    if ( strncmp(passwords[0], password, 2 ) == 0) {
        Serial.println("Correct PW");
        return true;
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
    Serial.println(Mother.STB_.rcvdPtr);
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
    Serial.println("stageaction");
    switch (stage) {
        case solved:
            Serial.println("solved");
            Mother.motherRelay.digitalWrite(relays::door, doorOpen);
            LED_CMDS::setStripToClr(Mother, ledBrain, LED_CMDS::clrGreen, 50, 1);
            MotherIO.setOuput(outSolved, true);
            delay(200);
            MotherIO.outputReset();
        break;
        case idle:
            Serial.println("idle");
            Mother.motherRelay.digitalWrite(relays::door, doorClosed);
            LED_CMDS::setStripToClr(Mother, ledBrain, LED_CMDS::clrBlue, 50, 1);
            MotherIO.outputReset();
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

    Serial.println(result);

    switch (result) {
        case inputValues::roomReset:
            Serial.println("reset");
            Mother.motherRelay.digitalWrite(relays::door, doorClosed);
            LED_CMDS::setStripToClr(Mother, ledBrain, LED_CMDS::clrBlack, 50, 1);
            MotherIO.outputReset();
            stage = stages::off;
        break;
        case inputValues::mcBoot:
            stage = stages::idle;
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
    if (stage == stages::idle) {
        validBrainResult = Mother.rs485PerformPoll(2);
        if (validBrainResult) {interpreter();}
    }
    handleInputs();    
    stageUpdate(); 
    delay(50);
    wdt_reset();
}
