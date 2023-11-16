#pragma once

#define PasswordAmount 1
#define MaxPassLen 4

#define doorOpen    0
#define doorClosed  1

#define relayAmount 1


enum brains {
    ledBrain = 2
};

enum stages {
    off = 1, 
    idle = 2, 
    solved = 4, 
};

char passwords[PasswordAmount][MaxPassLen] = {
    "AH"    // Rachel
};

int passwordMap[PasswordAmount] = {
    idle
};

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
    setSolved           
};

enum outputValues {
    outSolved = 1,
};

#define outputCnt 1
#define inputCnt 2

int intputArray[inputCnt] = {
    IO_1,
    IO_2,
};

int outputArray[outputCnt] = {
    IO_3                      
};


enum relays {
    door
};

enum relayInits {
    doorInit = doorClosed
};

int relayPinArray[relayAmount] = {
    door,
};

int relayInitArray[relayAmount] = {
    doorInit,
};
