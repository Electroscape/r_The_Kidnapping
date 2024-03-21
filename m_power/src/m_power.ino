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
            Mother.motherRelay.digitalWrite(relays::empore, closed);
            Mother.motherRelay.digitalWrite(relays::living, closed);
            Mother.motherRelay.digitalWrite(relays::room2, closed);
            Mother.motherRelay.digitalWrite(relays::service, closed);
        break;
        case inputValues::livingOn:
            Mother.motherRelay.digitalWrite(relays::living, open);
        break;
        case inputValues::livingOff:
            Mother.motherRelay.digitalWrite(relays::living, closed);
        break;
        case inputValues::emporeOn:
            Mother.motherRelay.digitalWrite(relays::empore, open);
        break;
        case inputValues::empporeOff:
            Mother.motherRelay.digitalWrite(relays::empore, closed);
        break;
        case inputValues::room2On:
            Mother.motherRelay.digitalWrite(relays::room2, open);
        break;
        case inputValues::room2Off:
            Mother.motherRelay.digitalWrite(relays::room2, closed);
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




