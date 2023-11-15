/**
 * @file m_waterLevels.cpp
 * @author Martin Pek (martin.pek@web.de)
 * @brief changes leds depending on water levels read out by reed sensors
 * @version 0.1
 * @date 2023-07-24
 * 
 * @copyright Copyright (c) 2022
 * 
 *  TODO: 
 */


#include <stb_mother.h>
#include <stb_mother_IO.h>
#include <stb_keypadCmds.h>
#include <stb_oledCmds.h>
#include <stb_mother_ledCmds.h>


#include "header_st.h"

STB_MOTHER Mother;
STB_MOTHER_IO MotherIO;

int lastState = -1;
int stage = stages::prestage;
int lastStage = -1;
bool hallwayLit = false;


// setup function too?
void toggleHallwayLight(bool state) {
    if (state == hallwayLit) { return; }

    // @todo implement
}

void handleInputs() {

    int result = MotherIO.getInputs();

    if (lastState == result) {
        return;
    }
    // result -= result & (1 << door_reed);

    // @todo is this always active?
    toggleHallwayLight(result & fuse_1);


    switch (stage) {
        case hallway: 
            if (result == (fuse_1 + fuse_2 + fuse_3)) {
                stage = stages::missionControlUnlock;
            }
        case stages::missionControlUnlock: {
            stage = stages::missionControlBoot;
        }
        case missionControlBoot: 
            if (result == (fuse_1 + fuse_2 + fuse_3 + fuse_4)) {
                stage = stages::completed;
            }
        break;
    }

    lastState = result;
    // if output being set wait 200ms 
}

void setup() {

    // starts serial and default oled
    Mother.begin();
    // Mother.relayInit(relayPinArray, relayInitArray, relayAmount);
    MotherIO.ioInit(intputArray, sizeof(intputArray), outputArray, sizeof(outputArray));

    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);
    Mother.rs485SetSlaveCount(0);
    // LED_CMDS::setAllStripsToClr(Mother, ledBrain, LED_CMDS::clrBlack, 100);
  
    wdt_reset();
    // delay(4000);
    // wdt_reset();
}


void stageActions() {
    wdt_reset();
    switch (stage) {
        case stages::prestage: break;
        case stages::hallway: 
            toggleHallwayLight(true);
            // kill alarm light
            // open the door
        break;
        case stages::missionControlUnlock: break;
        case stages::completed: break;
    }
}


void stageUpdate() {
    if (lastStage == stage) { return; }
    Serial.print("Stage is:");
    Serial.println(stage);
    stageActions();
    delay(200);
    MotherIO.outputReset();
}


void loop() {
    handleInputs();    
    stageUpdate(); 
    wdt_reset();
}




