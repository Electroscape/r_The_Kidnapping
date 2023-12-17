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
    livingOn,
    livingOff,
    mcOn,
    mcOff,
    bedroomOn,
    bedroomOff,           
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
    living,
    mc,
    bedroom, 
    relayAmount
};

enum relayInits {
    living_init = open,
    mc_init = open,
    bedroom_init = open,
};

int relayPinArray[relayAmount] = {
    living,
    mc,
    bedroom,
};

int relayInitArray[relayAmount] = {
    living_init,
    mc_init,
    bedroom_init,
};
