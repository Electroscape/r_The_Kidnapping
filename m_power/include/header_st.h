#pragma once

#define relayOn     0
#define relayOff     1

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
    room2On,
    room2Off,           
    serviceOn,           
    serviceOff,  
    chimneyOpening,                 
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
    room2,
    service,
    relayAmount
};

enum relayInits {
    empore_init = relayOff,
    living_init = relayOff,
    room2_init = relayOff,
    service_init = relayOff,
};

int relayPinArray[relayAmount] = {
    empore,
    living,
    room2,
    service,
};

int relayInitArray[relayAmount] = {
    empore_init,
    living_init,
    room2_init,
    service_init,
};
