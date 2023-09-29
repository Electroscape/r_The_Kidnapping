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
bool level1_active = false;
bool level3_active = false;
bool level3_complete = true;

unsigned long pumpCycleSwitch = millis();

int pumpPhase[2] = {0};
int pumpIntensity = 0;


void enableWdt() {
    wdt_enable(WDTO_8S);
}


void updatePumps() {

    if (pumpIntensity == 4) { return; }

    if (millis() > pumpCycleSwitch) {
        if (pumpPhase[0] == 0) {
            Mother.motherRelay.digitalWrite(pump_1, closed);
            Mother.motherRelay.digitalWrite(pump_2, closed);
        } else {
            Mother.motherRelay.digitalWrite(pump_1, open);
            Mother.motherRelay.digitalWrite(pump_2, open);
        }
        switch (pumpIntensity) {
            case 0:
                // 0 = false
                if (pumpPhase[0] == 0) {
                    pumpCycleSwitch = millis() + (unsigned long) 6000;
                } else {
                    pumpCycleSwitch = millis() + (unsigned long) 200;
                }
            break;
            case 1:
                if (pumpPhase[0] == 0) {
                    pumpCycleSwitch = millis() + (unsigned long) 2000;
                } else {
                    pumpCycleSwitch = millis() + (unsigned long) 350;
                }
            break;

            case 2:
                if (pumpPhase[0] == 0) {
                    pumpCycleSwitch = millis() + (unsigned long) 50;
                } else {
                    pumpCycleSwitch = millis() + (unsigned long) 800;
                }
            break;

            case 3:
                if (pumpPhase[0] == 0) {
                    pumpCycleSwitch = millis() + (unsigned long) 400;
                } else {
                    pumpCycleSwitch = millis() + (unsigned long) 500;
                }
            break;
        }
        if (pumpPhase[0]) {
            pumpPhase[0] = 0;
        } else {
            pumpPhase[0] = 1;
        }
    }
}


void handleInputs() {

    int result = MotherIO.getInputs();

    if (lastState == result) {
        return;
    }

    lastState = result;
    Serial.println(result);

    if (ledTable & result) {
        Mother.motherRelay.digitalWrite(table_light, open);
        Mother.motherRelay.digitalWrite(table_magnet, open);
    }

    if (level_1 & result) {
        if (!level1_active) {
            LED_CMDS::setAllStripsToClr(Mother, ledBrain, LED_CMDS::clrRed, 20);
            pumpIntensity = 0;
            pumpCycleSwitch = millis();
            level1_active = true;
            level3_active = false;
            level3_complete = false;
            Mother.motherRelay.digitalWrite(table_light, table_light_init);
            Mother.motherRelay.digitalWrite(table_magnet, table_magnet_init);
        }
    } else if (level1_active) {
        pumpIntensity = 1;
        pumpCycleSwitch = millis();
        level1_active = false;
        LED_CMDS::fade2color(Mother, ledBrain, LED_CMDS::clrRed, 20, LED_CMDS::clrRed, 60, 3000, 1);
        // LED_CMDS::setLEDToClr(Mother, ledBrain, LED_CMDS::clrRed, 100, 1, 0);
    }
   

    if (level_2 & result) {
        pumpIntensity = 2;
        pumpCycleSwitch = millis();
        LED_CMDS::fade2color(Mother, ledBrain, LED_CMDS::clrRed, 60, LED_CMDS::clrPurple, 80, 3000, 1);
    }

    if (level_3 & result) {
        if (!level3_active) {
            LED_CMDS::fade2color(Mother, ledBrain, LED_CMDS::clrPurple, 80, LED_CMDS::clrWhite, 20, 1500, 1);
            pumpIntensity = 3;
            pumpCycleSwitch = millis();
            level3_active = true;
            delay(300); // to make sure its not a hystersis 
        }
    } else if (level3_active and !level3_complete) {
        level3_complete = true;
        pumpCycleSwitch = millis();
        LED_CMDS::fade2color(Mother, ledBrain, LED_CMDS::clrWhite, 20, LED_CMDS::clrWhite, 5, 5000, 1);
        Mother.motherRelay.digitalWrite(pump_1, closed);
        Mother.motherRelay.digitalWrite(pump_2, closed);
        pumpIntensity = 4;
    }
}


void setup() {

    // starts serial and default oled
    Mother.begin();
    Mother.relayInit(relayPinArray, relayInitArray, relayAmount);
    MotherIO.ioInit(intputArray, sizeof(intputArray), outputArray, sizeof(outputArray));

    Serial.println("WDT endabled");
    enableWdt();
    Mother.rs485SetSlaveCount(0);
    LED_CMDS::setAllStripsToClr(Mother, ledBrain, LED_CMDS::clrBlack, 100);
  
    wdt_reset();
}


void loop() {
    handleInputs();    
    updatePumps();
    wdt_reset();
}




