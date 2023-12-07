#pragma once

#define StageCount 2
#define PasswordAmount 6
#define MaxPassLen 10
#define lockerCnt 4

// may aswell move this into the Oled lib?
#define headLineMaxSize 16

#define open   0
#define closed 1


enum brains {
    keypad,
    ledDot = 2,
    ledStrip = 3,
};

enum leds {
    hallway = 1,    
    living,    
    empore, 
};

enum strips {
    stripLiving = 1,
    missionControl,
};



enum relays {
    chinmey,
    relayAmount, 
};

enum relayInits {
    locker_1_init = closed,
};

int relayPinArray[relayAmount] = {
    chinmey,
};

int relayInitArray[relayAmount] = {
    locker_1_init,
};


#define inputCnt    7
#define outputCnt   1


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

enum IOValues {
    service_enable = 1,
    gameStart, 
    gameEndTrigger,     // triggered by breakout riddle everything goes green
    hallwayStart,
    hallwayOff,
    hallwayOn,
    hallwayDimmed,
    apartmentEnter,
    chimneyOverride,    // manual override trigger
    mcBoot,          // fusebox powering up MC via fuses
    waterUV,        // turns of the empore
    gameResetIn,
    gameOver,
    chinmeySolved = 1   // the one output we use
};

int intputArray[inputCnt] = {
    IO_1,
    IO_2,
    IO_3,
    IO_4,
    IO_5,
    IO_6,
    IO_7
};

int outputArray[outputCnt] = {
    IO_8
};

enum stages{
    idle = 1,
    chimneyOpening,
};

// the sum of all stages sprinkled with a bit of black magic
int stageSum = ~( ~0 << StageCount );


// could have multiple brains listed here making up a matrix
/*
int flagMapping[StageCount]{
    keypadFlag + oledFlag,
    keypadFlag + oledFlag,
    keypadFlag + oledFlag
};
*/


char passwords[PasswordAmount][MaxPassLen] = {
    "1234",
    "20162023",     // service code
};


// defines what password/RFIDCode is used at what stage, if none is used its -1
int passwordMap[PasswordAmount] = {
    stageSum,   // service code, valid in all stages
    stageSum,   // service code, valid in all stages
};


char stageTexts[StageCount][headLineMaxSize] = {
    "Access Code",
    "Access Code",
};
