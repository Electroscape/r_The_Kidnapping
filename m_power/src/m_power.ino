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
    Serial.print("Input: ");
    Serial.println(result);
    
    switch (result) {
        case inputValues::roomReset:
            Mother.motherRelay.digitalWrite(relays::empore, relayOff);
            Mother.motherRelay.digitalWrite(relays::living, relayOff);
            Mother.motherRelay.digitalWrite(relays::raum2, relayOff);
            Mother.motherRelay.digitalWrite(relays::service, relayOff);
        break;
        case inputValues::livingOn:
            Mother.motherRelay.digitalWrite(relays::living, relayOn);
        break;
        case inputValues::livingOff:
            Mother.motherRelay.digitalWrite(relays::living, relayOff);
        break;
        case inputValues::emporeOn:
            Mother.motherRelay.digitalWrite(relays::empore, relayOn);
        break;
        case inputValues::empporeOff:
            Mother.motherRelay.digitalWrite(relays::empore, relayOff);
        break;
        case inputValues::raum2On:
            Mother.motherRelay.digitalWrite(relays::raum2, relayOn);
        break;
        case inputValues::raum2Off:
            Mother.motherRelay.digitalWrite(relays::raum2, relayOff);
        break;
        case inputValues::emporeLivingOn:
            Mother.motherRelay.digitalWrite(relays::empore, relayOn);
            Mother.motherRelay.digitalWrite(relays::living, relayOn);
        break;
        case inputValues::emporeLivingOff:
            Mother.motherRelay.digitalWrite(relays::empore, relayOff);
            Mother.motherRelay.digitalWrite(relays::living, relayOff);
        break;
        case inputValues::mcBoot:
            Mother.motherRelay.digitalWrite(relays::empore, relayOff);
            Mother.motherRelay.digitalWrite(relays::living, relayOff);
            Mother.motherRelay.digitalWrite(relays::raum2, relayOn);
        break;
        case inputValues::serviceOn:
            Mother.motherRelay.digitalWrite(relays::service, relayOn);
            Mother.motherRelay.digitalWrite(relays::empore, relayOn);
            Mother.motherRelay.digitalWrite(relays::living, relayOn);
            Mother.motherRelay.digitalWrite(relays::raum2, relayOn);
        break;
        case inputValues::serviceOff:
            Mother.motherRelay.digitalWrite(relays::service, relayOff);
            Mother.motherRelay.digitalWrite(relays::empore, relayOff);
            Mother.motherRelay.digitalWrite(relays::living, relayOff);
            Mother.motherRelay.digitalWrite(relays::raum2, relayOff);
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




