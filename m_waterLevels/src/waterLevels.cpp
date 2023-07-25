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

    switch (result) {
        case level_1: 
            // Mother.motherRelay.digitalWrite(pump_1, closed);
            LED_CMDS::setLEDToClr(Mother, ledBrain, LED_CMDS::clrRed, 100, 1, 0);
            // static void setLEDToClr(STB_MOTHER &Mother,int brainNo , const int clr[3], int brightness,int stripNo, int LED_Nr);
        break;
        case level_2:
            LED_CMDS::setLEDToClr(Mother, ledBrain, LED_CMDS::clrGreen, 100, 1, 1);
        break;
        case level_3:
            LED_CMDS::setLEDToClr(Mother, ledBrain, LED_CMDS::clrGreen, 100, 1, 2);
        break;
        case level_4:
            LED_CMDS::setLEDToClr(Mother, ledBrain, LED_CMDS::clrGreen, 100, 1, 3);
        break;
        case level_5:
            LED_CMDS::setAllStripsToClr(Mother, ledBrain, LED_CMDS::clrPurple, 100);
        break;
        default: break;
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




