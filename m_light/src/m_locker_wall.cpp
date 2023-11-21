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
int stage = gameLive;
// since stages are single binary bits and we still need to d some indexing
int stageIndex = 0;
// doing this so the first time it updates the brains oled without an exta setup line
int lastStage = -1;
int lastInput = 0;
// going to use this to set the LEDs how they are intended to once the function necessary has been added to the lib
bool lockerStatuses[lockerCnt] = {false};


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

void ledUpdate() {
    for (int no=0; no<lockerCnt; no++) {
        if (lockerStatuses[no]) {
            LED_CMDS::setStripToClr(Mother, 1, LED_CMDS::clrGreen, 50, no);
        }
    }
}


void ledBlink() {
    wdt_reset();
    LED_CMDS::setAllStripsToClr(Mother, 1, LED_CMDS::clrRed);
    delay(200);
    LED_CMDS::setAllStripsToClr(Mother, 1, LED_CMDS::clrBlack);
    delay(200);
    LED_CMDS::setAllStripsToClr(Mother, 1, LED_CMDS::clrRed);
    delay(200);
    LED_CMDS::setAllStripsToClr(Mother, 1, LED_CMDS::clrBlack);
    delay(200);
    LED_CMDS::setAllStripsToClr(Mother, 1, LED_CMDS::clrRed, 50);
    // TODO: make a fncs that passes a clr array
    ledUpdate();
};


void stageActions() {
    wdt_reset();
    switch (stage) {
        case serviceMode: Mother.motherRelay.digitalWrite(service, open); break;
        case gameLive :Mother.motherRelay.digitalWrite(service, closed); break;
        case gameEnd:
            unsigned long startTime = millis();
            while ((millis() - startTime) < (unsigned long) 10200) {wdt_reset();}
            LED_CMDS::setAllStripsToClr(Mother, 1, LED_CMDS::clrBlack);
            startTime = millis(); 
            while ((millis() - startTime) < (unsigned long) 60000) {wdt_reset();}
            ledBlink();
            stage = gameLive;
        break;
    }
}


void gameReset() {
    for (int no=0; no<lockerCnt; no++) {
        lockerStatuses[no] = false;
        Mother.motherRelay.digitalWrite(no, closed);
    }
    LED_CMDS::setAllStripsToClr(Mother, 1, LED_CMDS::clrRed, 50);
}


/**
 * @brief  room specific section
 * @param passNo 
*/
void passwordActions(int passNo) {
    switch (stage) {
        case gameLive:
            switch (passNo) {
                case service: 
                    stage = serviceMode; 
                    gameReset();
                    MotherIO.setOuput(1 << 2);
                break;
                case resetIndex: 
                    gameReset();
                    stage = gameLive;
                break;
                default: 
                    lockerStatuses[passNo] = true;
                    delay(2);
                    Mother.motherRelay.digitalWrite(passNo, open);
                    ledUpdate();
                break;
            }
        break;
        case serviceMode:
            stage = gameLive;
            MotherIO.setOuput(1 << 3);
            gameReset();
        break;
    }
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

    /*
    Mother.STB_.dbgln("checkforKeypad");
    Mother.STB_.dbgln(Mother.STB_.rcvdPtr);
    */

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
    bool doBlink = false;
    if (passwordInterpreter(cmdPtr)) {
        sprintf(noString, "%d", KeypadCmds::correct);
        strcat(msg, noString);
    } else {
        sprintf(noString, "%d", KeypadCmds::wrong);
        strcat(msg, noString);
        doBlink = true;
    }
    // idk why but we had a termination poblem, maybe sprintf doesnt terminate?
    msg[strlen(msg) - 1] = '\0';

    strcat(msg, noString);
    Mother.sendCmdToSlave(msg);
    if (doBlink) { ledBlink(); }
    return true;
}


void interpreter() {
    while (Mother.nextRcvdLn()) {
        checkForKeypad();
    }
}


/**
 * @brief  triggers effects specific to the given stage, 
 * room specific excecutions can happen here
 * TODO: avoid reposts of setflags, but this is an optimisation
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
    Mother.setFlags(0, flagMapping[stageIndex]);

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

    // technicall 2 but no need to poll the 2nd as it only receives the colour
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
        case IOValues::service_enable: stage = serviceMode; break;
        case IOValues::service_disable: stage = gameLive; break;
        case IOValues::gameEndTrigger: stage = gameEnd; break;
    }
}


void loop() {
    Mother.rs485PerformPoll();
    interpreter();
    handleInputs();
    stageUpdate();
    wdt_reset();
}




