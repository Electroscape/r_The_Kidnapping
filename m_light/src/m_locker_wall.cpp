/**
 * @file m_access_mother.cpp
 * @author Martin Pek (martin.pek@web.de)
 * @brief 
 * @version 0.1
 * @date 2022-09-09
 * 
 * @copyright Copyright (c) 2022
 * 
 *  TODO: 
 *  - consider non blocking 
 */


#include <stb_mother.h>
#include <stb_keypadCmds.h>
#include <stb_mother_IO.h>
#include <stb_oledCmds.h>
#include <stb_mother_ledCmds.h>

#include "header_st.h"

STB_MOTHER_IO MotherIO;

STB_MOTHER Mother;
int stage = stages::chimneyOpening;
// since stages are single binary bits and we still need to d some indexing
int stageIndex = 0;
// doing this so the first time it updates the brains oled without an exta setup line
int lastStage = -1;
int lastInput = 0;


// since stages are binary bit being shifted we cannot use them to index
void setStageIndex() {
    for (int i=0; i<StageCount; i++) {
        if (stage <= 1 << i) {
            stageIndex = i;
            /*            
            Serial.print("stageIndex:");
            Serial.println(stageIndex);
            delay(1000);
            */
            return;
        }
    }
    Serial.println(F("STAGEINDEX ERRROR!"));
    delay(16000);
}


void gameReset() {
    Mother.motherRelay.digitalWrite(relays::chinmey, closed);
    stage = stages::idle;
}


/**
 * @brief  room specific section
 * @param passNo 
*/
void passwordActions(int passNo) {
    stage = stages::chimneyOpening;
}


bool passwordInterpreter(char* password) {
    Mother.STB_.defaultOled.clear();
    for (int passNo=0; passNo < PasswordAmount; passNo++) {
        if (passwordMap[passNo] & stage) {
            if ( strlen(passwords[passNo]) == strlen(password) &&
                strncmp(passwords[passNo], password, strlen(passwords[passNo]) ) == 0) 
            {
                passwordActions(passNo);
                delay(500);
                MotherIO.outputReset();
                return true;
            }
        }
    }
    return false;
}



// candidate to be moved to a mother specific part of the keypad lib
bool checkForKeypad() {

    if (strncmp(keypadCmd.c_str(), Mother.STB_.rcvdPtr, keypadCmd.length()) != 0) {
        return false;
    }
    Mother.sendAck();

    char *cmdPtr = strtok(Mother.STB_.rcvdPtr, KeywordsList::delimiter.c_str());
    cmdPtr = strtok(NULL, KeywordsList::delimiter.c_str());
    int cmdNo;
    sscanf(cmdPtr, "%d", &cmdNo);

    /* no evaluation requested, may just be an update for oled display on mother
    * or being used for things like an interface
    */
    if (cmdNo != KeypadCmds::evaluate) { return true; }

    cmdPtr = strtok(NULL, KeywordsList::delimiter.c_str());
    if (!(cmdPtr != NULL)) {
        return false;
    }

    // prepare return msg with correct or incorrect
    char msg[10] = "";
    char noString[3] = "";
    strcpy(msg, keypadCmd.c_str());
    strcat(msg, KeywordsList::delimiter.c_str());
    if (passwordInterpreter(cmdPtr)) {
        sprintf(noString, "%d", KeypadCmds::correct);
        strcat(msg, noString);
    } else {
        sprintf(noString, "%d", KeypadCmds::wrong);
        strcat(msg, noString);
    }
    // idk why but we had a termination poblem, maybe sprintf doesnt terminate?
    msg[strlen(msg) - 1] = '\0';

    strcat(msg, noString);
    Mother.sendCmdToSlave(msg);

    return true;
}


void interpreter() {
    while (Mother.nextRcvdLn()) {
        checkForKeypad();
    }
}


void stageActions() {
    switch (stage) {
        case stages::chimneyOpening: 
            Mother.motherRelay.digitalWrite(relays::chinmey, open);
        break;
        case stages::idle: 
        break;
    }
}


/**
 * @brief  triggers effects specific to the given stage, 
 * room specific excecutions can happen here
*/
void stageUpdate() {
    if (lastStage == stage) { return; }
    setStageIndex();
        
    // check || stageIndex >= int(sizeof(stages))
    if (stageIndex < 0 || stageIndex > 1 << StageCount) {
        Serial.println(F("Stages out of index!"));
        delay(5000);
        wdt_reset();
    }
    // Mother.setFlags(0, flagMapping[stageIndex]);

    char msg[32] = "";
    strcpy(msg, oledHeaderCmd.c_str());
    strcat(msg, KeywordsList::delimiter.c_str());
    strcat(msg, stageTexts[stageIndex]); 
    Mother.sendCmdToSlave(msg);

    lastStage = stage;
    stageActions();
}


void setup() {
    // starts serial and default oled
    Mother.begin();
    Mother.relayInit(relayPinArray, relayInitArray, relayAmount);
    MotherIO.ioInit(intputArray, sizeof(intputArray), outputArray, sizeof(outputArray));

    Serial.println(F("WDT endabled"));
    wdt_enable(WDTO_8S);

    Mother.rs485SetSlaveCount(1);
    gameReset();
    wdt_reset();
}

void handleInputs() {
    int inputVal = MotherIO.getInputs(true);
    if (lastInput == inputVal) {
        return;
    }
    // Serial.print("received input:");
    // Serial.println(inputVal);

    lastInput = inputVal;
    switch (inputVal) {
        case IOValues::service_enable: stage = 0; break;
    }
}


void loop() {
    Mother.rs485PerformPoll();
    interpreter();
    handleInputs();
    stageUpdate();
    wdt_reset();
}




