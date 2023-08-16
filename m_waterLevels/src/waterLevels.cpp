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


void enableWdt() {
    wdt_enable(WDTO_8S);
}



void handleInputs() {

    int result = MotherIO.getInputs();

    if (lastState == result) {
        return;
    }
    lastState = result;
    Serial.println(result);

    if (ledTable & result) {
        Mother.motherRelay.digitalWrite(lightTable, open);
    }

    if (level_1 & result) {
        if (!level1_active) {
            LED_CMDS::setAllStripsToClr(Mother, ledBrain, LED_CMDS::clrBlack, 100);
            Mother.motherRelay.digitalWrite(pump_1, closed);
            Mother.motherRelay.digitalWrite(pump_2, closed);
            level1_active = true;
            Mother.motherRelay.digitalWrite(lightTable, closed);
        }
    } else if (level1_active) {
        level1_active = false;
        LED_CMDS::setLEDToClr(Mother, ledBrain, LED_CMDS::clrRed, 100, 1, 0);
    }
   

    if (level_2 & result) {
        LED_CMDS::setLEDToClr(Mother, ledBrain, LED_CMDS::clrGreen, 100, 1, 1);
    }
    if (level_3 & result) {
        LED_CMDS::setAllStripsToClr(Mother, ledBrain, LED_CMDS::clrPurple, 100);
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
    wdt_reset();
}




