/**
 * @file m_power.cpp
 * @author Martin Pek (martin.pek@web.de)
 * @brief mother to handle power outlets
 * @version 0.1
 * @date 2023-12-17
 * 
 * @copyright Copyright (c) 2022
 * 
 *  TODO: 
 */


#include <stb_mother.h>
#include <stb_mother_IO.h>


#include "header_st.h"

STB_MOTHER Mother;
STB_MOTHER_IO MotherIO;

int lastState = 0;


void enableWdt() {
    wdt_enable(WDTO_8S);
}

void handleInputs() {

    int result = MotherIO.getInputs();

    if (lastState == result) {
        return;
    }

    switch (result) {
        case inputValues::roomReset:
            Mother.motherRelay.digitalWrite(relays::mc, closed);
            Mother.motherRelay.digitalWrite(relays::living, closed);
            Mother.motherRelay.digitalWrite(relays::bedroom, closed);
        break;
        case inputValues::mcOn:
            Mother.motherRelay.digitalWrite(relays::mc, open);
        break;
        case inputValues::mcOff:
            Mother.motherRelay.digitalWrite(relays::mc, closed);
        break;
        case inputValues::livingOn:
            Mother.motherRelay.digitalWrite(relays::mc, open);
        break;
        case inputValues::livingOff:
            Mother.motherRelay.digitalWrite(relays::mc, closed);
        break;
        case inputValues::bedroomOn:
            Mother.motherRelay.digitalWrite(relays::bedroom, open);
        break;
        case inputValues::bedroomOff:
            Mother.motherRelay.digitalWrite(relays::bedroom, closed);
        break;
    }

    lastState = result;
    Serial.println(result);
}


void setup() {

    // starts serial and default oled
    Mother.begin();
    Mother.relayInit(relayPinArray, relayInitArray, relayAmount);
    MotherIO.ioInit(intputArray, sizeof(intputArray), outputArray, sizeof(outputArray));

    Serial.println("WDT endabled");
    enableWdt();
    Mother.rs485SetSlaveCount(0);
    wdt_reset();
}


void loop() {
    handleInputs();    
    wdt_reset();
}




