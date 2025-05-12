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
 * 🔲 
 * ✅ 
 * ✅ 
 */


#include <stb_mother.h>
#include <stb_keypadCmds.h>
#include <stb_mother_IO.h>
#include <stb_oledCmds.h>
#include <stb_mother_ledCmds.h>

#include "header_st.h"

STB_MOTHER_IO MotherIO;

STB_MOTHER Mother;
int stage = stages::idle;
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
            return;
        }
    }
    Serial.println(F("STAGEINDEX ERRROR!"));
    delay(16000);
}


void gameReset() {
    Mother.motherRelay.digitalWrite(relays::chinmey, closed);
    LED_CMDS::setAllStripsToClr(Mother, brains::ledDot, LED_CMDS::clrBlack);
    LED_CMDS::setAllStripsToClr(Mother, brains::ledStrip, LED_CMDS::clrBlack);
    delay(100);
    LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrRed, 50, ledsIndex::zwinger);
    Mother.motherRelay.digitalWrite(relays::mcAlarm, closed);
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
            wdt_disable();
            MotherIO.setOuput(IOValues::chinmeySolved);
            delay(200);
            LED_CMDS::fade2color(Mother, brains::ledStrip, LED_CMDS::clrwarmerWhite, 50, LED_CMDS::clrBlack, 0, 2000, strips::stripLiving);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrwarmWhite, 50, LED_CMDS::clrBlack, 0, 2000, ledsIndex::empore);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrwarmWhite, 50, LED_CMDS::clrBlack, 0, 2000, ledsIndex::living);
            //LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrwarmerWhite, 50, LED_CMDS::clrBlack, 0, 2000, ledsIndex::hallway);
            delay(2000);
            LED_CMDS::setAllStripsToClr(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, ledsIndex::empore);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, ledsIndex::living);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrRed, 50, ledsIndex::zwinger);
            MotherIO.outputReset();
            delay(2000);
            Mother.motherRelay.digitalWrite(relays::chinmey, open);
            delay(5000);
            LED_CMDS::fade2color(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmerWhite, 50, 6000, strips::stripLiving);
            delay(100);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmWhite, 50, 6000, ledsIndex::empore);
            delay(100);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmWhite,50, 6000, ledsIndex::living);
            //LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmerWhite,50, 6000, ledsIndex::hallway);
            wdt_enable(WDTO_8S);
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
    if (lastInput == inputVal || inputVal == 0) {
        return;
    }
    
    Serial.print("received input:");
    Serial.println(inputVal);

    lastInput = inputVal;
    switch (inputVal) {
        case IOValues::service_enable: 
            stage = 0; 
            LED_CMDS::setAllStripsToClr(Mother, brains::ledDot, LED_CMDS::clrWhite, 50);
            LED_CMDS::setAllStripsToClr(Mother, brains::ledStrip, LED_CMDS::clrWhite, 50);
        break;
        case IOValues::gameEndTrigger: 
            LED_CMDS::setAllStripsToClr(Mother, brains::ledDot, LED_CMDS::clrGreen, 100);
            LED_CMDS::setAllStripsToClr(Mother, brains::ledStrip, LED_CMDS::clrGreen, 100);
            Mother.motherRelay.digitalWrite(relays::mcAlarm, closed);
        break;
        case IOValues::hallwayOff: LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, ledsIndex::hallway); break;
        case IOValues::hallwayOn: LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrwarmerWhite, 50, ledsIndex::hallway); break;
        case IOValues::hallwayStart: 
            LED_CMDS::blinking(Mother, brains::ledDot, LED_CMDS::clrRed, LED_CMDS::clrGreen, 500, 500, 5, 70, ledsIndex::hallway);
            delay(3000);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrwarmerWhite, 10, ledsIndex::hallway);
        break;
        case IOValues::apartmentEnter: 
            wdt_disable();
            //LED_CMDS::setStripToClr(Mother, brains::ledStrip, LED_CMDS::clrBlue, 0, strips::stripLiving);
            LED_CMDS::fade2color(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmerWhite, 50, 8000, strips::stripLiving);
            //delay(8000);
            //LED_CMDS::setStripToClr(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0, strips::stripLiving);
            //delay(1000);
            //LED_CMDS::setStripToClr(Mother, brains::ledStrip, LED_CMDS::clrWhite, 0, strips::stripLiving);
            //LED_CMDS::fade2color(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0, LED_CMDS::clrWhite, 50, 60000, strips::stripLiving);
            //delay(5000);
            //LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrWhite, 50, ledsIndex::living);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmWhite, 30, 8000, ledsIndex::living);
            delay(5000);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmWhite, 30, 10000, ledsIndex::empore);
            //LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrWhite, 50, ledsIndex::empore);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrwarmerWhite, 50, ledsIndex::hallway); 
            //delay(10);
            wdt_enable(WDTO_8S);
        break;
        case IOValues::chimneyOverride: stage=stages::chimneyOpening; break;
        case IOValues::mcBoot: 
            wdt_disable();
            LED_CMDS::setStripToClr(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0, strips::stripLiving); 
            LED_CMDS::blinking(Mother,brains::ledDot, LED_CMDS::clrBlack, LED_CMDS::clrBlue, 500, 500, 5, 70, ledsIndex::hallway);
            LED_CMDS::blinking(Mother,brains::ledDot, LED_CMDS::clrBlack, LED_CMDS::clrBlue, 500, 500, 5, 70, ledsIndex::empore);
            LED_CMDS::blinking(Mother,brains::ledDot, LED_CMDS::clrBlack, LED_CMDS::clrBlue, 500, 500, 5, 70, ledsIndex::living);
            delay(2500);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, ledsIndex::hallway); 
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, ledsIndex::empore); 
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, ledsIndex::living); 
            LED_CMDS::fade2color(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0, LED_CMDS::clrBlue, 50, 6000, strips::missionControl);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrBlue, 30, 6000, ledsIndex::empore);
            delay(8000);
            LED_CMDS::setStripToClr(Mother, brains::ledStrip, LED_CMDS::clrBlue, 50, strips::missionControl);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrBlue, 50, ledsIndex::empore);
            wdt_enable(WDTO_8S);
            //LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrbrightWhite, 50, 8000, ledsIndex::hallway);
            //LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmWhite, 30, 8000, ledsIndex::living);
            //LED_CMDS::fade2color(Mother, brains::ledStrip, LED_CMDS::clrBlack, 0, LED_CMDS::clrwarmerWhite, 50, 8000, strips::stripLiving);
        break;
        case IOValues::waterUV:
            Mother.motherRelay.digitalWrite(relays::mcAlarm, open);
            LED_CMDS::fade2color(Mother, brains::ledStrip, LED_CMDS::clrwarmerWhite, 50, LED_CMDS::clrwarmerWhite, 10, 1000, strips::stripLiving);
            delay(100);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrBlue, 50, LED_CMDS::clrBlack, 0, 1000, ledsIndex::empore);
            delay(100);
            LED_CMDS::fade2color(Mother, brains::ledDot, LED_CMDS::clrwarmWhite, 30, LED_CMDS::clrwarmWhite, 10, 1000, ledsIndex::living);
            delay(100);
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrGreen, 70, ledsIndex::zwinger);
        break;
        case IOValues::gameResetIn: 
            gameReset();
        break;
        case IOValues::hallwayGreen: 
            LED_CMDS::setStripToClr(Mother, brains::ledDot, LED_CMDS::clrGreen, 50, ledsIndex::hallway);
        break;
        case IOValues::gameOver:
            LED_CMDS::setAllStripsToClr(Mother, brains::ledDot, LED_CMDS::clrRed, 50);
            LED_CMDS::setAllStripsToClr(Mother, brains::ledStrip, LED_CMDS::clrRed, 50);
            Mother.motherRelay.digitalWrite(relays::mcAlarm, closed);
            Mother.motherRelay.digitalWrite(relays::chinmey, open);
        break;
    }

    delay(1500);
    wdt_reset();
}


void loop() {
    Mother.rs485PerformPoll();
    interpreter();
    handleInputs();
    stageUpdate();
    wdt_reset();
}

