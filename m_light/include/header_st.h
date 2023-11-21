#pragma once

#define StageCount 3
#define PasswordAmount 6
#define MaxPassLen 10
#define lockerCnt 4

// may aswell move this into the Oled lib?
#define headLineMaxSize 16

#define open   0
#define closed 1

enum relays {
    locker_1,
    locker_2,
    locker_3,
    locker_4,
    service, 
    relayAmount, 
};

enum relayInits {
    locker_1_init = closed,
    locker_2_init = closed,
    locker_3_init = closed,
    locker_4_init = closed,
    service_init = closed
};

int relayPinArray[relayAmount] = {
    locker_1,
    locker_2,
    locker_3,
    locker_4,
    service
};

int relayInitArray[relayAmount] = {
    locker_1_init,
    locker_2_init,
    locker_3_init,
    locker_4_init,
    service_init
};

#define inputCnt    2
#define outputCnt   2

enum IOpins {
    IO_1,
    IO_2,
    IO_3,
    IO_4,
};

enum IOValues {
    service_enable = 1,
    service_disable, 
    gameEndTrigger
};

int intputArray[inputCnt] = {
    IO_1,
    IO_2,
};

int outputArray[outputCnt] = {
    IO_3,
    IO_4,
};

enum stages{
    gameLive = 1,
    serviceMode = 2, 
    gameEnd = 4
};

// the sum of all stages sprinkled with a bit of black magic
int stageSum = ~( ~0 << StageCount );


// could have multiple brains listed here making up a matrix
int flagMapping[StageCount]{
    keypadFlag + oledFlag,
    keypadFlag + oledFlag,
    keypadFlag + oledFlag
};
// save what already is turned on on the brain so we do not need to send it again
int devicesOn = 0;

char passwords[PasswordAmount][MaxPassLen] = {
    "0983",
    "3105",
    "5638",
    "2018",
    "20162023",     // service code
    "0000",     // reset code, does this also work within th service mode?
};

const int resetIndex = service + 1;


// defines what password/RFIDCode is used at what stage, if none is used its -1
int passwordMap[PasswordAmount] = {
    gameLive,
    gameLive,
    gameLive,
    gameLive,
    stageSum,   // service code, valid in all stages
    gameLive    // reset code
};
// make a mapping of what password goes to what stage


char stageTexts[StageCount][headLineMaxSize] = {
    "Access Code",
    "Service Mode",
    ""
};
