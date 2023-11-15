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

int stage = stages::solved;
int stageIndex = 0;
int lastStage = -1;

// int inputTicks = 0;

int validBrainResult = 0;



/*
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
*/

/**
 * @brief Set the Stage Index object
 * @todo safety considerations
*/
void setStageIndex() {
    for (int i=0; i<StageCount; i++) {
        if (stage <= 1 << i) {
            stageIndex = i;
            Serial.print("stageIndex:");
            Serial.println(stageIndex);
            delay(1000);
            return;
        }
    }
    Serial.println(F("STAGEINDEX ERRROR!"));
    wdt_reset();
    delay(16000);
}


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
    handleResult();
    wdt_reset();
    return true;
}


void interpreter() {
    while (Mother.nextRcvdLn()) {
        checkForRfid();
    }
}


void stageActions() {
    wdt_reset();
    switch (stage) {
    }
}


void stageUpdate() {
    if (lastStage == stage) { return; }
    Serial.print("Stage is:");
    Serial.println(stage);
    setStageIndex();
        
    // check || stageIndex >= int(sizeof(stages))
    if (stageIndex < 0) {
        Serial.println(F("Stages out of index!"));
        delay(15000);
        
    }
    // important to do this before stageActions! otherwise we skip stages
    lastStage = stage;

    // for now no need to make it work properly scaling, need to build afnc repertoir anyways
    for (int brainNo=0; brainNo < Mother.getSlaveCnt(); brainNo++) {
        Mother.setFlags(brainNo, flagMapping[stageIndex]);
        delay(5);
    }
    MotherIO.outputReset();
    stageActions();
}


void inputInit() {
    for (int pin=0; pin<inputCnt; pin++) {
        inputPCF.begin(RESET_I2C_ADD);
        inputPCF.pinMode((uint8_t) pin, INPUT);
        inputPCF.digitalWrite((uint8_t) pin, HIGH);
    }
}


void handleInputs() {
    int result = MotherIO.getInputs();
    if (result == 0) { return; }

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

    setStageIndex();
    inputInit();

    wdt_reset();
    delay(1000);
}


void loop() {
    validBrainResult = Mother.rs485PerformPoll();
    if (validBrainResult) {interpreter();}
    handleInputs();    
    stageUpdate(); 
    wdt_reset();
}
