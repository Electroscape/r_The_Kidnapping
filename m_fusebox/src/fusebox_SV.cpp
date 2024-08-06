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


bool getLightBool(int result=MotherIO.getInputs()) {
    return ((result & fuse_1) > 0);
}

// setup function too?
void toggleHallwayLight(bool state) {
    if (state == hallwayLit || state != getLightBool()) { return; }
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
    if (stage != stages::hallway) { return; } 

    if ((result & lid_reed) == 0 && !alarmOn) {

        // getting some false positives, waiting and checking again
        delay(200);
        if ((MotherIO.getInputs() & lid_reed) > 0) { return; } 

        Serial.println("lid open");
        alarmOn = true;
        Mother.motherRelay.digitalWrite(relais::alarm, open);
    }
}


void handleInputs() {

    int result = MotherIO.getInputs();
    toggleHallwayLight(result);

    if (lastState == result) { return; }
    lastState = result;

    handleAlarm(result);
    if (result & mc_opened) {
        stage = stages::missionControlBoot;
        return;
    }
    if (result & inputs::start_game) {
        stage = stages::hallway;
        return;
    }

    result -= result & inputs::lid_reed;
    result -= result & inputs::mc_opened;
    result -= result & inputs::start_game;

    switch (stage) {
        case hallway: 
            if (result == (fuse_1 + fuse_2 + fuse_3)) {
                Mother.motherRelay.digitalWrite(relais::door, closed);  // since this is 90% of the game its closed -> open door
                Mother.motherRelay.digitalWrite(relais::doorOutput, open);
                Mother.motherRelay.digitalWrite(relais::alarm, alarm_init);
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
            Mother.motherRelay.digitalWrite(relais::door, open);
        break;
        case stages::missionControlUnlock: 
            Mother.motherRelay.digitalWrite(relais::alarm, closed);
        break;
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
    delay(5);
}




