#pragma once

#define open      0
#define closed      1

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
    empore_init = open,
    living_init = open,
    room2_init = open,
    service_init = open,
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
