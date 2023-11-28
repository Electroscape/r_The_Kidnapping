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
bool alarmOn = false;


// setup function too?
void toggleHallwayLight(bool state) {
    if (state == hallwayLit) { return; }
    if (state) {
        Mother.motherRelay.digitalWrite(relais::toggleOn, open);
    } else {
        Mother.motherRelay.digitalWrite(relais::toggleOff, open);
    }
    delay(100);
    Mother.motherRelay.digitalWrite(relais::toggleOn, closed);
    Mother.motherRelay.digitalWrite(relais::toggleOff, closed);
    hallwayLit = state;

    // @todo implement
}


void handleAlarm(int result) {
    if (stage > hallway || alarmOn) { return; } 
    if (result & lid_reed) {
        Mother.motherRelay.digitalWrite(relais::alarm, open);
    }
}


void handleInputs() {

    int result = MotherIO.getInputs();
    Serial.println(result);
    delay(300);

    if (lastState == result) {
        return;
    }

    handleAlarm(result);
    if (result & mc_opened) {
        stage = stages::missionControlBoot;
        return;
    }
    if (result & inputs::start_game) {
        stage = stages::hallway;
        return;
    }

    result -= result & lid_reed;
    result -= result & inputs::mc_opened;
    result -= result & inputs::start_game;

    // @todo is this always active?
    toggleHallwayLight(result & fuse_1);


    switch (stage) {
        case hallway: 
            if (result == (fuse_1 + fuse_2 + fuse_3)) {
                Mother.motherRelay.digitalWrite(relais::door, open);
                Mother.motherRelay.digitalWrite(relais::doorOutput, open);
                Mother.motherRelay.digitalWrite(relais::alarm, closed);
                delay(200);
                Mother.motherRelay.digitalWrite(relais::doorOutput, closed);
                alarmOn = false;
                stage = stages::missionControlUnlock;
            }
        break;
        case missionControlBoot: 
            if (result == (fuse_1 + fuse_2 + fuse_3 + fuse_4)) {
                stage = stages::completed;
            }
        break;
    }

    lastState = result;
}


void setup() {

    // starts serial and default oled
    Mother.begin();
    Mother.relayInit(relayPinArray, relayInitArray, relayAmount);
    MotherIO.ioInit(intputArray, sizeof(intputArray), outputArray, sizeof(outputArray));

    Serial.println("WDT endabled");
    wdt_enable(WDTO_8S);

    wdt_reset();
}


void stageActions() {
    wdt_reset();
    switch (stage) {
        case stages::prestage: break;
        case stages::hallway: 
            Mother.motherRelay.digitalWrite(relais::door, closed);
            Mother.motherRelay.digitalWrite(relais::alarm, closed);
        break;
        case stages::missionControlUnlock: break;
        case stages::completed: 
            Mother.motherRelay.digitalWrite(relais::mcBoot, open);
            delay(200);
            Mother.motherRelay.digitalWrite(relais::mcBoot, closed);
        break;
    }
}


void stageUpdate() {
    if (lastStage == stage) { return; }
    Serial.print("Stage is:");
    Serial.println(stage);
    stageActions();
    lastStage = stage;
    delay(200);
    MotherIO.outputReset();
}


void loop() {
    handleInputs();    
    stageUpdate(); 
    wdt_reset();
}




