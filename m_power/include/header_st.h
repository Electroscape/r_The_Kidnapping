#pragma once

#define relayOn     0
#define relayOff    1

enum IOpins {
    IO_1,
    IO_2,
    IO_3,
    IO_4,
    IO_5, 
    IO_6,
    IO_7,                       
    IO_8,                                            
};

enum inputValues {  
    roomReset = 1,
    emporeOn,
    empporeOff,
    livingOn,
    livingOff,
    emporeLivingOn,
    raum2On, // chimney light
    emporeLivingOff,  
    raum2Off,          
    serviceOn,           
    serviceOff,
    mcBoot = 15, // is 3 + 5 + 7          
};

enum outputValues {};

#define outputCnt 0
#define inputCnt 8

int intputArray[inputCnt] = {
    IO_1,
    IO_2,
    IO_3,
    IO_4,
    IO_5,
    IO_6,
    IO_7,
    IO_8,
};

int outputArray[outputCnt] = {};


enum relays {
    empore,
    living,
    raum2,
    service,
    relayAmount
};

enum relayInits {
    empore_init = relayOff,
    living_init = relayOff,
    raum2_init = relayOff,
    service_init = relayOff,
};

int relayPinArray[relayAmount] = {
    empore,
    living,
    raum2,
    service,
};

int relayInitArray[relayAmount] = {
    empore_init,
    living_init,
    raum2_init, // chemney light
    service_init,
};
